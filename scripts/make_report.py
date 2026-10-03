"""Generate the DefenceLens hackathon submission PDF (5-6 pages)."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak,
    Table, TableStyle, KeepTogether,
)

NAVY = HexColor("#0f172a")
BLUE = HexColor("#2563eb")
SLATE = HexColor("#475569")
LIGHT = HexColor("#eff6ff")
BORDER = HexColor("#cbd5e1")
GREEN = HexColor("#15803d")

W, H = A4
OUT = "DefenceLens-report.pdf"

styles = getSampleStyleSheet()


def st(name, **kw):
    s = ParagraphStyle(name, parent=styles["Normal"], fontName="Helvetica", fontSize=10,
                       leading=14, textColor=NAVY)
    for k, v in kw.items():
        setattr(s, k, v)
    return s


title = st("t", fontName="Helvetica-Bold", fontSize=34, leading=40, textColor=white,
           alignment=TA_CENTER)
subtitle = st("s", fontSize=14, leading=20, textColor=HexColor("#bfdbfe"), alignment=TA_CENTER)
h1 = st("h1", fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=BLUE,
        spaceBefore=6, spaceAfter=8)
h2 = st("h2", fontName="Helvetica-Bold", fontSize=12, leading=16, textColor=NAVY,
        spaceBefore=8, spaceAfter=4)
body = st("b", spaceAfter=6)
small = st("sm", fontSize=9, leading=12, textColor=SLATE)
cell = st("c", fontSize=8.5, leading=11)
cellb = st("cb", fontSize=8.5, leading=11, fontName="Helvetica-Bold")
mono = st("m", fontName="Courier-Bold", fontSize=9.5, leading=13, textColor=GREEN)


def cover(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)
    canvas.setFillColor(BLUE)
    canvas.rect(0, H - 14 * mm, W, 14 * mm, fill=1, stroke=0)
    canvas.rect(0, 0, W, 10 * mm, fill=1, stroke=0)
    canvas.restoreState()


def page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(BLUE)
    canvas.rect(0, H - 6 * mm, W, 6 * mm, fill=1, stroke=0)
    canvas.setFillColor(SLATE)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(18 * mm, 10 * mm, "DefenceLens — HackYeah 2026 · DEFENCE challenge")
    canvas.drawRightString(W - 18 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


frame = Frame(18 * mm, 18 * mm, W - 36 * mm, H - 34 * mm, id="f")
doc = BaseDocTemplate(OUT, pagesize=A4,
                      pageTemplates=[PageTemplate(id="cover", frames=[frame], onPage=cover),
                                     PageTemplate(id="page", frames=[frame], onPage=page)])

story = []

# ---------- Page 1: Cover ----------
story += [
    Spacer(1, 55 * mm),
    Paragraph("DefenceLens", title),
    Spacer(1, 8 * mm),
    Paragraph("Security monitoring that small organizations can actually run", subtitle),
    Spacer(1, 4 * mm),
    Paragraph("logs → detectors → incidents → evidence → impact → recommendations → verification",
              st("tag", fontSize=10, textColor=HexColor("#93c5fd"), alignment=TA_CENTER)),
    Spacer(1, 30 * mm),
    Paragraph("HackYeah 2026 · DEFENCE challenge", st("ev", fontSize=12, textColor=white,
              alignment=TA_CENTER, fontName="Helvetica-Bold")),
    Spacer(1, 4 * mm),
    Paragraph("Team: ______________ · Members: ______________",
              st("tm", fontSize=11, textColor=HexColor("#bfdbfe"), alignment=TA_CENTER)),
]
from reportlab.platypus import NextPageTemplate
story.insert(0, NextPageTemplate("page"))
story.append(PageBreak())

# ---------- Page 2: Problem & Solution ----------
story.append(Paragraph("The problem", h1))
story.append(Paragraph(
    "Small organizations — volunteer centers, NGOs, local services — run critical coordination "
    "infrastructure (request portals, volunteer accounts, logistics) with <b>no security staff and "
    "no budget</b>. When their API starts failing or an account is brute-forced, nobody notices "
    "until the service is down, and even then nobody knows what to do next. Enterprise SIEMs assume "
    "analysts, cloud subscriptions, and endless tuning; they are out of reach.", body))
story.append(Paragraph("Who faces it", h2))
story.append(Paragraph(
    "Our realistic scenario: a small volunteer center coordinating aid requests. One non-expert "
    "operator. A disrupted request API blocks aid intake; a compromised coordinator account "
    "endangers the whole community it serves.", body))
story.append(Paragraph("Our solution", h1))
story.append(Paragraph(
    "<b>DefenceLens</b> is a self-hosted monitoring and resilience tool that turns raw logs into "
    "plain-language incidents a non-expert can act on. Each incident shows <b>facts, explicit "
    "limitations, a timeline, evidence, and the impact on the organization's services</b> — e.g. "
    "\"API errors are blocking request submission\". The operator records an action, and the system "
    "<b>verifies the outcome</b> against subsequent events, honestly reporting \"insufficient "
    "data\" when it cannot tell.", body))
feats = [
    ("Detect earlier", "4 detectors: failed-login bursts, suspicious success after failures, attack signatures (traversal, .env/.git, SQLi, wp-admin), 5xx error-rate growth vs baseline."),
    ("Understand impact", "Service dependency mapping: an incident shows which service is hit and what it blocks for the organization."),
    ("Reduce consequences", "Plain-language recommendations, action tracking, and outcome verification close the loop from alert to fix."),
    ("Harden supply chain", "Built-in Trivy image scanning (never executes the image) + an operator-confirmed deployment flow with required grounds."),
    ("Stay honest", "Open attention-index formula, explicit limitations on every incident, synthetic demo data always tagged."),
]
rows = [[Paragraph(f"<b>{a}</b>", cellb), Paragraph(b, cell)] for a, b in feats]
t = Table(rows, colWidths=[38 * mm, 136 * mm])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (0, -1), LIGHT),
    ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("LEFTPADDING", (0, 0), (-1, -1), 6),
]))
story.append(t)
story.append(PageBreak())

# ---------- Page 3: 20 gaps ----------
story.append(Paragraph("20 weaknesses of existing solutions — and how we close them", h1))
story.append(Paragraph(
    "Compared against today's typical options for this audience: enterprise SIEMs (Splunk, "
    "Microsoft Sentinel), open-source stacks (ELK, Wazuh), and standalone scanners.", small))
story.append(Spacer(1, 2 * mm))
gaps = [
    ("Require dedicated analysts", "Plain-language facts, limitations, next steps"),
    ("Per-GB / license pricing", "Fully open-source, runs on one small host"),
    ("Days of installation & tuning", "One docker compose up — minutes to running"),
    ("Alert floods, no priorities", "15-min episodes with P1/P2/P3 severity"),
    ("Alerts without evidence", "Up to 200 linked evidence events + timeline"),
    ("No link to business impact", "Impact view: affected service & what it blocks"),
    ("Overconfident verdicts", "Explicit limitations: hypotheses, not proof"),
    ("No follow-through after alert", "\"Verify outcome\" re-analyzes post-action events"),
    ("Opaque risk scores", "Open, documented attention-index formula"),
    ("Silent loss of malformed logs", "Accepted / duplicate / rejected shown separately"),
    ("Duplicates skew stats on retry", "Idempotent ingest: (source, SHA256(event_id))"),
    ("Pipelines lose data on restart", "Disk buffers, acks, durable pending scans"),
    ("Vuln scanning sold separately", "Built-in Trivy: real CVEs, components, secrets"),
    ("Scanners trust untrusted images", "Image never run; non-root worker, no caps"),
    ("CVE found ≠ fix deployed", "Deployment confirmation requiring grounds"),
    ("Late logs break detection windows", "±10 min re-evaluation for late events"),
    ("Static error-rate thresholds", "Volume + share ≥30% + ≥20 pp growth vs baseline"),
    ("Dashboards hide the math", "Every chart links to its calculation"),
    ("Demo data mixed with real data", "Synthetic data explicit and tagged; DB starts empty"),
    ("Undefined degraded mode", "Waiting/error/retry states; ingest survives outages"),
]
rows = [[Paragraph("<b>#</b>", cellb), Paragraph("<b>Weakness of existing tools</b>", cellb),
         Paragraph("<b>DefenceLens</b>", cellb)]]
rows += [[Paragraph(str(i + 1), cell), Paragraph(a, cell), Paragraph(b, cell)]
         for i, (a, b) in enumerate(gaps)]
t = Table(rows, colWidths=[8 * mm, 80 * mm, 86 * mm], repeatRows=1)
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), BLUE),
    ("TEXTCOLOR", (0, 0), (-1, 0), white),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT]),
    ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
]))
story.append(t)
story.append(PageBreak())

# ---------- Page 4: Architecture ----------
story.append(Paragraph("Architecture & resilience by design", h1))
arch = [
    ("Ingest", "Vector agent or direct HTTP (JSONL / Nginx access.log). Disk buffers, acknowledgements, retries, file checkpoints — logs survive restarts."),
    ("API & analysis", "FastAPI + Pydantic + SQLAlchemy/Alembic on PostgreSQL 16. Detection runs synchronously on ingest; no LLM in the hot path."),
    ("Scanning", "RQ worker runs only the Trivy binary with fixed arguments. Uploaded image is never executed; no Docker socket; non-root, no-new-privileges, no capabilities, 2 CPU / 2 GiB."),
    ("Durability", "Pending scans persisted in PostgreSQL; a dispatcher reconciles with RQ every 5 s and re-queues after Redis recovery. Redis AOF + persistent volumes."),
    ("Frontend", "React + TypeScript + Vite, TanStack Query (5 s polling), Recharts, Tailwind. Shows waiting / error / retry states explicitly."),
]
rows = [[Paragraph(f"<b>{a}</b>", cellb), Paragraph(b, cell)] for a, b in arch]
t = Table(rows, colWidths=[30 * mm, 144 * mm])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (0, -1), LIGHT),
    ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
story.append(t)
story.append(Paragraph("Designed for incomplete information & limited resources", h2))
story.append(Paragraph(
    "Without a traffic baseline, the error detector records a high level but explicitly refuses to "
    "confirm growth. Without post-action events, outcome verification answers \"insufficient "
    "data\" instead of guessing. If Redis or the network fails, ingestion continues and scans "
    "resume after recovery. Absence of logs is never treated as absence of threats.", body))
story.append(Paragraph("Detectors (transparent rules, no black box)", h2))
story.append(Paragraph(
    "• 5 login failures from one IP/user within 5 minutes.<br/>"
    "• Successful login by the same pair after ≥5 failures — possible compromise.<br/>"
    "• HTTP attack signatures: path traversal, .env/.git probing, SQL union select, script injection, wp-admin scans.<br/>"
    "• Error surge: ≥10 HTTP events, ≥5×5xx, share ≥30%, growth ≥20 pp vs the preceding window.", body))
story.append(Paragraph(
    "Attention index: P1=25 · P2=12 · P3=5, weighted by service importance, plus up to 15 for the "
    "confirmed image's CVEs; capped at 100. It is a prioritization aid, not a probability of compromise.", small))
story.append(PageBreak())

# ---------- Page 5: Demo ----------
story.append(Paragraph("Live demo in 5 minutes", h1))
story.append(Paragraph("Prerequisites: Docker Engine + Compose. Nothing else on the host.", body))
story.append(Paragraph("cp .env.example .env && docker compose up -d --build", mono))
story.append(Paragraph("Web UI: http://localhost:18080 · API: http://localhost:18000/docs", small))
story.append(Spacer(1, 2 * mm))
steps = [
    ("1. Sign in & load demo", "Use the API token; click \"Load demo\". Synthetic data is created only explicitly and tagged — the DB starts empty."),
    ("2. Overview", "Four detectors fire; the attention index and chart appear. Open the calculation explanation — every number is auditable."),
    ("3. Incident deep-dive", "Open the API-errors incident: facts, limitations, timeline, evidence, and impact — API downtime blocks aid request intake."),
    ("4. Act & verify", "Save an \"In progress\" action with a note. \"Verify outcome\" analyzes events after the action and reports honestly."),
    ("5. Real logs & streaming", "Upload JSONL or Nginx access.log; counters show accepted/duplicate/rejected. Append to demo/logs/live.jsonl — Vector streams it live."),
    ("6. Image scanning", "Upload a docker save archive; Trivy reports real CVEs, components, and potential secrets without ever running the image."),
    ("7. Deployment confirmation", "Confirm a fix with required grounds (CI digest or deployment record) — clearly an operator statement, not auto-verification."),
]
rows = [[Paragraph(f"<b>{a}</b>", cellb), Paragraph(b, cell)] for a, b in steps]
t = Table(rows, colWidths=[42 * mm, 132 * mm])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (0, -1), LIGHT),
    ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
story.append(t)
story.append(Paragraph("Quality checks included", h2))
story.append(Paragraph(
    "Isolated API/rule tests (pytest), an end-to-end integration script against the real DB with "
    "concurrent delivery and Vector, and a Playwright browser smoke test.", body))
story.append(PageBreak())

# ---------- Page 6: Value, honesty, disclosure ----------
story.append(Paragraph("Implementation value & honest boundaries", h1))
story.append(Paragraph("Ready for real use", h2))
story.append(Paragraph(
    "DefenceLens deploys today on a single small host that an NGO already owns. The entire stack is "
    "open source, ports default to localhost, and every security-relevant behavior (idempotency, "
    "retries, sandboxing of scans) is implemented, not planned. It fits where a SIEM never will: "
    "zero license cost, one operator, minutes to deploy.", body))
story.append(Paragraph("What we deliberately do not claim", h2))
story.append(Paragraph(
    "Single trusted operator (no RBAC yet); in-memory window analysis targets small event streams, "
    "not SIEM-scale volumes; a CVE does not prove exploitation; temporal proximity does not prove "
    "causality; confirmed deployment is an operator statement with grounds. Production hardening "
    "(TLS, retention, backups, stronger auth) is documented in the README.", body))
story.append(Paragraph("Roadmap", h2))
story.append(Paragraph(
    "Multi-user roles and audit trail · notification channels (e-mail/Telegram) · retention "
    "policies · more detectors (DNS, phishing-link verification) · shared threat indicators "
    "between organizations.", body))
story.append(Paragraph("AI & resource disclosure", h2))
story.append(Paragraph(
    "Built during HackYeah with the help of AI coding assistants (GitHub Copilot) for development "
    "and documentation. Open-source components used under their licenses: Trivy, Vector, FastAPI, "
    "PostgreSQL, Redis, RQ, React, Vite, Tailwind, Recharts. The team understands and can defend "
    "every technical decision in the solution.", body))
story.append(Spacer(1, 6 * mm))
t = Table([[Paragraph(
    "<b>DefenceLens</b> — detect earlier, understand impact, act with confidence.<br/>"
    "Repository: github.com/NINEZERN/monitoring · Demo: docker compose up → localhost:18080",
    st("fin", fontSize=11, leading=16, textColor=white, alignment=TA_CENTER))]],
    colWidths=[174 * mm])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), NAVY),
    ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
]))
story.append(t)

doc.build(story)
print("OK", OUT)
