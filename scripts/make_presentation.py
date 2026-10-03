#!/usr/bin/env python3
"""DefenceLens HackYeah deck: diagrams + 20-gaps story. python3 scripts/make_presentation.py"""
import os
from reportlab.lib.colors import HexColor, white
from reportlab.pdfgen import canvas

W, H = 1280, 720

BG = HexColor("#f8fafc")
PANEL = HexColor("#e8eef5")
BORDER = HexColor("#cbd5e1")
ACCENT = HexColor("#0369a1")
ACCENT2 = HexColor("#059669")
TEXT = HexColor("#1e293b")
MUTED = HexColor("#64748b")
RED = HexColor("#b91c1c")
REDBG = HexColor("#fee2e2")
GREENBG = HexColor("#d1fae5")

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "DefenceLens-presentation.pdf")
c = canvas.Canvas(OUT, pagesize=(W, H))
c.setTitle("DefenceLens — HackYeah 2026")
PAGE = [0]


def new():
    PAGE[0] += 1
    if PAGE[0] > 1:
        c.showPage()
    c.setFillColor(BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 10)
    c.drawString(40, 20, "DefenceLens — HackYeah 2026 — OPEN TASK: DEFENCE")
    c.drawRightString(W - 40, 20, str(PAGE[0]))


def title(t, sub=None):
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 32)
    c.drawString(60, H - 72, t)
    c.setStrokeColor(ACCENT)
    c.setLineWidth(3)
    c.line(60, H - 86, 60 + c.stringWidth(t, "Helvetica-Bold", 32), H - 86)
    if sub:
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 15)
        c.drawString(60, H - 110, sub)


def box(x, y, w, h, label, sub="", fill=white, border=BORDER, tcol=ACCENT, fs=15):
    c.setFillColor(fill)
    c.setStrokeColor(border)
    c.setLineWidth(1.5)
    c.roundRect(x, y, w, h, 8, fill=1, stroke=1)
    c.setFillColor(tcol)
    c.setFont("Helvetica-Bold", fs)
    lines = label.split("\n")
    base = y + h / 2 + (len(lines) - 1) * (fs / 2 + 2) + (10 if sub else 0) - fs / 2 + 4
    for i, ln in enumerate(lines):
        c.drawCentredString(x + w / 2, base - i * (fs + 4), ln)
    if sub:
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 11)
        for i, ln in enumerate(sub.split("\n")):
            c.drawCentredString(x + w / 2, base - len(lines) * (fs + 4) + 2 - i * 13, ln)


def arrow(x1, y1, x2, y2, col=MUTED, lw=2):
    c.setStrokeColor(col)
    c.setFillColor(col)
    c.setLineWidth(lw)
    c.line(x1, y1, x2, y2)
    import math
    ang = math.atan2(y2 - y1, x2 - x1)
    s = 9
    p = c.beginPath()
    p.moveTo(x2, y2)
    p.lineTo(x2 - s * math.cos(ang - 0.45), y2 - s * math.sin(ang - 0.45))
    p.lineTo(x2 - s * math.cos(ang + 0.45), y2 - s * math.sin(ang + 0.45))
    p.close()
    c.drawPath(p, fill=1, stroke=0)


def bullets(items, x=70, y=None, size=16, gap=40, bold_head=True):
    y = y if y is not None else H - 150
    for head, rest in items:
        c.setFillColor(ACCENT2)
        c.setFont("Helvetica-Bold", size)
        c.drawString(x, y, "•")
        c.setFillColor(TEXT)
        c.setFont("Helvetica-Bold" if bold_head else "Helvetica", size)
        c.drawString(x + 20, y, head)
        if rest:
            c.setFillColor(MUTED)
            c.setFont("Helvetica", size - 1)
            c.drawString(x + 24 + c.stringWidth(head, "Helvetica-Bold", size), y, rest)
        y -= gap
    return y


# ============ 1. TITLE ============
new()
c.setFillColor(ACCENT)
c.setFont("Helvetica-Bold", 62)
c.drawCentredString(W / 2, H - 230, "DefenceLens")
c.setFillColor(TEXT)
c.setFont("Helvetica", 25)
c.drawCentredString(W / 2, H - 280, "Security monitoring that small organizations can actually run")
# mini pipeline diagram on title
steps = ["logs", "detectors", "incidents", "evidence", "impact", "verification"]
bw, bh, gap = 150, 46, 32
total = len(steps) * bw + (len(steps) - 1) * gap
x0 = (W - total) / 2
y0 = H - 390
for i, s in enumerate(steps):
    x = x0 + i * (bw + gap)
    box(x, y0, bw, bh, s, fill=white if i % 2 == 0 else PANEL, fs=15)
    if i:
        arrow(x - gap + 4, y0 + bh / 2, x - 4, y0 + bh / 2, col=ACCENT)
c.setFillColor(ACCENT2)
c.setFont("Helvetica-Bold", 18)
c.drawCentredString(W / 2, 190, "HackYeah 2026 · OPEN TASK: DEFENCE")
c.setFillColor(TEXT)
c.setFont("Helvetica", 16)
c.drawCentredString(W / 2, 158, "Team: Borys · Hlieb · Eduard · Aknur")
c.setFillColor(MUTED)
c.setFont("Helvetica", 13)
c.drawCentredString(W / 2, 128, "github.com/NINEZERN/monitoring")

# ============ 2. PROBLEM ============
new()
title("The problem", "The people least able to afford an incident are the least protected")
bullets([
    ("NGOs & volunteer centers run critical infrastructure", "— request portals, accounts — with zero security staff."),
    ("Nobody notices an attack until the service is down.", "Then nobody knows what to do next."),
    ("Enterprise tools assume experts and money.", "Per-GB pricing, multi-day setup, alert floods, opaque scores."),
], gap=44)
# diagram: small org vs enterprise wall
y0 = 150
box(80, y0, 320, 170, "Small organization", "1 operator, no budget,\nno security training", fill=white)
box(880, y0, 320, 170, "Enterprise SIEM", "analysts required\n$$$ per GB · weeks of tuning", fill=REDBG, tcol=RED)
c.setFillColor(RED)
c.setFont("Helvetica-Bold", 44)
c.drawCentredString(640, y0 + 95, "✕  unreachable  ✕")
c.setFillColor(MUTED)
c.setFont("Helvetica", 14)
c.drawCentredString(640, y0 + 55, "cost · complexity · expertise gap")

# ============ 3. CORE IDEA ============
new()
title("Our approach", "We studied 20 real weaknesses of existing tools — and built the system that closes them")
cols = [
    ("Existing tools (SIEM / ELK / Wazuh / Splunk)", RED, REDBG, [
        "Alerts that require an analyst to decode",
        "Alert floods, no prioritization",
        "Verdicts without evidence or impact",
        "Overconfident: \u201cyou are compromised\u201d",
        "Closed scores, hidden math",
        "Silent data loss, lost pipelines",
        "Scanning sold as a separate product",
    ]),
    ("DefenceLens", ACCENT2, GREENBG, [
        "Plain-language facts, limitations, next steps",
        "15-min episodes with P1/P2/P3 severity",
        "200 evidence events + business impact per incident",
        "Hypotheses, honesty, \u201cinsufficient data\u201d verdicts",
        "Open, documented attention-index formula",
        "Idempotent ingest, disk buffers, visible counters",
        "Built-in Trivy scanning — image never executed",
    ]),
]
for i, (head, col, bgc, rows) in enumerate(cols):
    x = 70 + i * 590
    box(x, 130, 550, 420, "", fill=bgc, border=col)
    c.setFillColor(col)
    c.setFont("Helvetica-Bold", 19)
    c.drawString(x + 24, 510, head)
    c.setFillColor(TEXT)
    c.setFont("Helvetica", 15)
    yy = 472
    for r in rows:
        c.setFillColor(col)
        c.drawString(x + 24, yy, "✕" if i == 0 else "✓")
        c.setFillColor(TEXT)
        c.drawString(x + 46, yy, r)
        yy -= 46
arrow(640, 340, 680, 340, col=ACCENT, lw=4)

# ============ 4-5. 20 GAPS TABLE ============
GAPS = [
    ("Needs dedicated analysts to read alerts", "Incidents as plain-language facts, limitations, next steps"),
    ("Per-GB licensing costs", "Fully open-source; runs on one small host"),
    ("Multi-day install & tuning", "docker compose up — minutes to a working system"),
    ("Alert floods, no priorities", "15-min episodes with P1/P2/P3 severity"),
    ("Alerts without evidence", "Up to 200 linked evidence events + timeline per incident"),
    ("No link between alert and business impact", "Impact view: affected service & what it blocks"),
    ("Overconfident verdicts", "Explicit limitations: signatures are hypotheses, not proof"),
    ("Alert closed, problem unverified", "Verify-outcome re-analysis; honest \u201cinsufficient data\u201d"),
    ("Opaque risk scores", "Open attention-index formula (P1=25/P2=12/P3=5 × importance)"),
    ("Silent loss on malformed logs", "Accepted / duplicate / rejected counters; errors returned"),
    ("Retries duplicate events", "Idempotent ingest: unique (source_id, SHA256(event_id))"),
    ("Pipeline loses data on restarts", "Vector disk buffers + acks; durable scans in PostgreSQL"),
    ("Vuln scanning is a separate product", "Built-in Trivy: CVEs, components, potential secrets"),
    ("Scanners trust untrusted images", "Image never run; non-root worker, no Docker socket"),
    ("No link from CVE to deployed fix", "Deployment confirmation with grounds (CI digest/record)"),
    ("Late logs break detection windows", "Late events re-evaluate a ±10-minute window"),
    ("Static 5xx thresholds", "Volume + share ≥30% + growth ≥20 pp vs baseline"),
    ("Dashboards hide the math", "Every chart links to its calculation"),
    ("Demo data mixed with real data", "Synthetic loaded only explicitly, tagged; DB starts empty"),
    ("Undefined degraded mode", "Waiting/error/retry states; ingest continues while scans wait"),
]


def gaps_slide(rows, start, part):
    new()
    title(f"20 weaknesses of existing tools → closed ({part})")
    y = H - 140
    rh = 27
    # header
    c.setFillColor(RED)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, y, "Weakness in existing solutions")
    c.setFillColor(ACCENT2)
    c.drawString(650, y, "DefenceLens answer")
    y -= 14
    for k, (weak, fix) in enumerate(rows):
        yy = y - (k + 1) * rh + 8
        if k % 2 == 0:
            c.setFillColor(PANEL)
            c.rect(60, yy - 7, W - 120, rh, fill=1, stroke=0)
        c.setFillColor(MUTED)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(68, yy, f"{start + k}")
        c.setFillColor(TEXT)
        c.setFont("Helvetica", 12.5)
        c.drawString(100, yy, weak)
        c.setFillColor(ACCENT)
        c.drawString(620, yy, "→")
        c.setFillColor(TEXT)
        c.drawString(650, yy, fix)


gaps_slide(GAPS[:10], 1, "1 / 2")
gaps_slide(GAPS[10:], 11, "2 / 2")

# ============ 6. SYSTEM ARCHITECTURE ============
new()
title("System architecture", "Boring, proven, fully open-source — one compose file")
# layout
#  sources -> vector -> api -> postgres
#                        api -> redis -> worker(trivy)
#  browser -> nginx/react -> api
box(60, 420, 190, 90, "Log sources", "app logs · nginx\naccess.log · JSONL", fill=PANEL, tcol=TEXT)
box(310, 420, 190, 90, "Vector", "disk buffers · acks\ncheckpoints", fill=white)
box(560, 400, 210, 130, "FastAPI core", "ingest · idempotency\n4 detectors · episodes\nattention index", fill=GREENBG, tcol=ACCENT2)
box(850, 470, 180, 80, "PostgreSQL 16", "events · episodes\npending scans")
box(850, 360, 180, 80, "Redis + RQ", "scan queue · AOF")
box(1080, 360, 150, 80, "Trivy worker", "non-root\nno Docker socket")
box(310, 240, 190, 80, "React UI", "Vite · Recharts\n5s polling", fill=white)
box(60, 240, 190, 80, "Operator", "one person\nno training", fill=PANEL, tcol=TEXT)
box(560, 240, 210, 80, "Dispatcher", "reconciles queue\nevery 5 s · re-queues", fill=white)
arrow(250, 465, 306, 465, col=ACCENT)
arrow(500, 465, 556, 465, col=ACCENT)
arrow(770, 490, 846, 505, col=ACCENT)
arrow(770, 440, 846, 405, col=ACCENT)
arrow(1030, 400, 1076, 400, col=ACCENT)
arrow(250, 280, 306, 280, col=ACCENT)
arrow(500, 280, 556, 280, col=ACCENT)
arrow(665, 324, 665, 396, col=ACCENT)
arrow(940, 356, 760, 300, col=MUTED)
c.setFillColor(MUTED)
c.setFont("Helvetica", 12)
c.drawString(790, 318, "recovery after Redis outage")
c.setFillColor(TEXT)
c.setFont("Helvetica", 14)
c.drawString(60, 170, "Durability: ack only after PostgreSQL commit · Vector disk buffers · Redis AOF · persistent volumes.")
c.drawString(60, 144, "Security: user images are never executed · manifest validated before unpack · secret values never stored.")
c.drawString(60, 118, "Tested: isolated API/rule tests · integration suite on the real stack · Playwright browser smoke test.")

# ============ 7. DETECTION PIPELINE ============
new()
title("Detection pipeline", "Deterministic and explainable — no LLM in the detection path")
flow = [
    ("Ingest", "JSONL / array\nnginx logs"),
    ("Normalize +\ndeduplicate", "SHA256(event_id)\nper-service lock"),
    ("4 detectors", "sync, in-window\n±10 min late events"),
    ("Episodes", "15-min merge\nP1/P2/P3 · reopen"),
    ("Incident", "facts · limitations\nimpact · evidence"),
    ("Verify", "post-action\nre-analysis"),
]
bw, bh, g = 180, 100, 22
x0 = (W - (len(flow) * bw + (len(flow) - 1) * g)) / 2
y0 = H - 270
for i, (name, sub) in enumerate(flow):
    x = x0 + i * (bw + g)
    box(x, y0, bw, bh, name, sub, fill=GREENBG if i in (2, 3) else white,
        tcol=ACCENT2 if i in (2, 3) else ACCENT, fs=15)
    if i:
        arrow(x - g + 3, y0 + bh / 2, x - 3, y0 + bh / 2, col=ACCENT)
bullets([
    ("Brute force:", "5 login failures from one IP/user in 5 minutes."),
    ("Suspicious success:", "login succeeds after ≥5 failures by the same pair in 5 minutes."),
    ("HTTP signatures:", "traversal, .env/.git, SQL union select, script, wp-admin."),
    ("5xx surge:", "≥10 events / ≥5 errors / share ≥30% / growth ≥20 pp vs previous window; missing baseline is stated."),
], y=330, gap=42)

# ============ 8. HONESTY ============
new()
title("Honest by design", "The system tells the operator what it cannot know")
bullets([
    ("Signatures are hypotheses, not proof of breach.", ""),
    ("Absence of logs does not mean absence of threats.", ""),
    ("A CVE does not prove exploitation;", "temporal proximity does not prove causality."),
    ("\u201cInsufficient data\u201d is a first-class verdict,", "not a hidden failure."),
    ("Deployment confirmation is an operator statement with grounds,", "never silent automation."),
    ("Synthetic demo data is explicit and tagged;", "the database starts empty."),
], gap=46)
box(70, 110, W - 140, 90, "", fill=PANEL)
c.setFillColor(ACCENT)
c.setFont("Helvetica-Bold", 17)
c.drawCentredString(W / 2, 165, "Attention index — open formula, not a magic score")
c.setFillColor(TEXT)
c.setFont("Helvetica", 15)
c.drawCentredString(W / 2, 135, "P1=25 · P2=12 · P3=5, × service importance/5, + up to 15 for the confirmed image; capped at 100.")

# ============ 9. CLOSING ============
new()
title("Try it in 5 minutes")
box(70, H - 300, 620, 120, "", fill=PANEL)
c.setFillColor(ACCENT2)
c.setFont("Courier-Bold", 19)
c.drawString(100, H - 228, "cp .env.example .env")
c.drawString(100, H - 258, "docker compose up -d --build")
c.setFillColor(TEXT)
c.setFont("Helvetica", 16)
yy = H - 350
for ln in [
    "Web UI: http://localhost:18080   ·   API docs: http://localhost:18000/docs",
    "Load demo → explicit synthetic data · upload your own logs or a docker save archive",
    "No Node, Python, or Trivy needed on the host.",
]:
    c.drawString(70, yy, ln)
    yy -= 30
box(760, H - 460, 450, 280, "Built during HackYeah",
    "FastAPI · PostgreSQL 16 · Redis/RQ\nVector · Trivy · React/Vite/Tailwind\n\n"
    "API + rule tests · integration suite\nPlaywright browser smoke test",
    fill=white, fs=18)
c.setFillColor(ACCENT)
c.setFont("Helvetica-Bold", 26)
c.drawString(70, 130, "DefenceLens — defence that fits in one compose file.")
c.setFillColor(MUTED)
c.setFont("Helvetica", 15)
c.drawString(70, 98, "Borys · Hlieb · Eduard · Aknur — HackYeah 2026 — github.com/NINEZERN/monitoring")

c.save()
print("Wrote", OUT)
