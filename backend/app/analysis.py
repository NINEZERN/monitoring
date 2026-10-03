"""Deterministic rules. Event-time windows, no LLM or automatic response."""
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import unquote
from sqlalchemy import select
from app.models import Event, Incident, Service, now

NGINX = re.compile(r'^(?P<ip>\S+) \S+ \S+ \[(?P<time>[^]]+)\] "(?P<method>\S+) (?P<path>.*?) HTTP/[^"]+" (?P<status>\d{3}) ')
SUSPICIOUS = re.compile(r"\.\./|/\.env(?:$|\?)|/\.git|union\s+select|<script|/etc/passwd|/wp-admin", re.I)

def utc(value):
    if isinstance(value, datetime):
        dt = value
    else:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("timestamp must include timezone")
    return dt.astimezone(timezone.utc).isoformat()

def normalize(raw):
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            m = NGINX.match(raw)
            if not m:
                raise ValueError("expected JSON object or Nginx combined/common access log")
            d = m.groupdict()
            raw = dict(timestamp=datetime.strptime(d["time"], "%d/%b/%Y:%H:%M:%S %z").isoformat(),
                       ip=d["ip"], method=d["method"], path=d["path"], status=int(d["status"]))
    if not isinstance(raw, dict):
        raise ValueError("event must be an object")
    # Vector file source wraps the original line in message.
    if "message" in raw and "status" not in raw and "event" not in raw:
        return normalize(raw["message"])
    if not raw.get("timestamp"):
        raise ValueError("timestamp is required; event time must not be invented")
    ts = utc(raw["timestamp"])
    if datetime.fromisoformat(ts) > datetime.now(timezone.utc) + timedelta(minutes=5):
        raise ValueError("timestamp is more than 5 minutes in the future")
    data = {k: raw[k] for k in ("event_id", "ip", "user", "method", "path", "status", "event", "message", "synthetic") if k in raw}
    for k in ("event_id", "ip", "user", "method", "path", "event", "message"):
        if k in data:
            if not isinstance(data[k], str) or len(data[k]) > 8192:
                raise ValueError(f"{k}: expected string up to 8192 characters")
    if "status" in data:
        data["status"] = int(data["status"])
        if not 100 <= data["status"] <= 599:
            raise ValueError("invalid HTTP status")
    data["timestamp"] = ts
    key = str(data.get("event_id")) if data.get("event_id") else json.dumps(data, sort_keys=True, ensure_ascii=False)
    return data, hashlib.sha256(key.encode()).hexdigest()

def analyze(db, service_id, start, end):
    service = db.get(Service, service_id)
    # Include the baseline before and follow-up after late-arriving events.
    lo = (datetime.fromisoformat(start) - timedelta(minutes=10)).isoformat()
    hi = (datetime.fromisoformat(end) + timedelta(minutes=10)).isoformat()
    events = list(db.scalars(select(Event).where(Event.service_id == service_id, Event.timestamp >= lo, Event.timestamp <= hi).order_by(Event.timestamp, Event.id)))
    for e in events:
        t = datetime.fromisoformat(e.timestamp)
        window = [x for x in events if t - timedelta(minutes=5) <= datetime.fromisoformat(x.timestamp) <= t]
        d = e.data
        principal = (d.get("ip"), d.get("user"))
        failures = [x for x in window if x.data.get("event") == "login_failed" and (x.data.get("ip"), x.data.get("user")) == principal]
        if d.get("event") == "login_failed" and len(failures) >= 5 and any(principal):
            record(db, service, "failed_logins", e, failures, principal, "Серия неудачных входов", "P2",
                   [f"{len(failures)} отказов входа за 5 минут; IP: {d.get('ip', 'нет данных')}, учётная запись: {d.get('user', 'нет данных')}"],
                   ["Возможен подбор пароля; ошибки пользователя также возможны."],
                   ["Проверьте источник запросов и владельца учётной записи.", "При подтверждении подбора ограничьте частоту входов и включите MFA."])
        if d.get("event") == "login_success" and len(failures) >= 5 and any(principal):
            record(db, service, "success_after_failures", e, failures + [e], principal, "Вход после серии отказов", "P1",
                   [f"Успешный вход после {len(failures)} отказов за 5 минут для того же IP и пользователя."],
                   ["Учётная запись могла быть скомпрометирована; успешный вход сам по себе этого не доказывает."],
                   ["Свяжитесь с владельцем учётной записи и проверьте активную сессию.", "Если вход не признан, отзовите сессию и смените секреты вручную."])
        if SUSPICIOUS.search(unquote(unquote(d.get("path", "")))):
            record(db, service, "suspicious_http", e, [e], d.get("ip"), "Подозрительный HTTP-запрос", "P2",
                   [f"Запрос соответствует сигнатуре: {d.get('method', 'HTTP')} {d.get('path')}"],
                   ["Возможно автоматическое сканирование; выполнение атаки не установлено."],
                   ["Проверьте код ответа, журналы приложения и доступ к запрошенному ресурсу.", "Закройте доступ к служебным файлам и проверьте правила gateway."])
        current = [x for x in window if "status" in x.data]
        baseline = [x for x in events if t - timedelta(minutes=10) <= datetime.fromisoformat(x.timestamp) < t - timedelta(minutes=5) and "status" in x.data]
        errors = [x for x in current if x.data["status"] >= 500]
        ratio = len(errors) / len(current) if current else 0
        old = sum(x.data["status"] >= 500 for x in baseline) / len(baseline) if baseline else None
        if len(current) >= 10 and len(errors) >= 5 and ratio >= .3 and (old is None or ratio >= old + .2):
            facts = [f"5xx: {len(errors)}/{len(current)} ({ratio:.0%}) за 5 минут."]
            facts += [f"Предыдущие 5 минут: {old:.0%} ошибок."] if old is not None else ["Базовый период отсутствует: установлен высокий уровень, рост не доказан."]
            record(db, service, "server_errors", e, current, "service", "Рост / высокий уровень ошибок API", "P1" if service.importance >= 4 else "P2", facts,
                   ["Возможен сбой приложения или зависимости; связь с другими событиями по времени не доказывает причину."],
                   ["Проверьте доступность API и базы данных, начните с health-check.", "Сопоставьте ошибки с развёртываниями; откат рассматривайте только после проверки.", "После действий проверьте новые логи и отправку тестовой заявки."])

def record(db, service, detector, event, evidence, principal, title, priority, facts, hypotheses, recommendations):
    # Deduplicate overlapping detections within a 15-minute event-time episode.
    recent = db.scalar(select(Incident).where(Incident.service_id == service.id, Incident.detector == detector,
        Incident.fingerprint.like(hashlib.sha256(json.dumps(principal, sort_keys=True).encode()).hexdigest() + ":%"),
        Incident.created_at >= (datetime.fromisoformat(event.timestamp) - timedelta(minutes=15)).isoformat(),
        Incident.created_at <= event.timestamp).order_by(Incident.created_at.desc()))
    ids = list(dict.fromkeys([x.id for x in evidence]))
    limitations = ["Правила анализируют только полученные логи; отсутствие событий не означает отсутствие угроз.", "CVE и совпадение времени не являются доказательством взлома или причины сбоя."]
    if recent:
        added = set(ids) - set(recent.evidence_ids)
        recent.evidence_ids = list(dict.fromkeys(recent.evidence_ids + ids))[-200:]
        recent.facts = facts
        recent.updated_at = now()
        if added and recent.status == "resolved":
            recent.status = "open"
        return
    fp = hashlib.sha256(json.dumps(principal, sort_keys=True).encode()).hexdigest() + ":" + detector + ":" + service.id + ":" + event.id
    db.add(Incident(fingerprint=fp, service_id=service.id, detector=detector, title=title, priority=priority,
        created_at=event.timestamp, evidence_ids=ids[-200:], facts=facts, hypotheses=hypotheses,
        limitations=limitations + ["В карточке хранится до 200 доказательств; полный поток доступен в журнале."], recommendations=recommendations))
    db.flush()
