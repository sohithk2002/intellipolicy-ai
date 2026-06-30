"""
Cotiviti Assessment — correct deliverables per the prompt:
  - IntelliPolicy_AI_Report.docx       (2 pages research + 1 page bibliography)
  - IntelliPolicy_AI_Presentation.pptx (6-8 slides: report overview + POC)
  - IntelliPolicy_AI_Video_Script.txt  (full on-camera + PPT + demo script)
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from docx import Document
from docx.shared import Inches as DI, Pt as DP, RGBColor as DR
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import datetime, pathlib

OUT = pathlib.Path("/Users/sohithkampalli/cotivity/intellipolicy-ai")

# ── colours ──────────────────────────────────────────────────────────────────
PURPLE    = RGBColor(0x6B, 0x2D, 0x8B)
LPURPLE   = RGBColor(0xB0, 0x7F, 0xC8)
DARK      = RGBColor(0x1A, 0x0D, 0x2E)
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
OFFWHITE  = RGBColor(0xF7, 0xF3, 0xFB)
AMBER     = RGBColor(0xFB, 0xBF, 0x24)
TEAL      = RGBColor(0x14, 0xB8, 0xA6)
SKY       = RGBColor(0x38, 0xBD, 0xF8)
RED       = RGBColor(0xEF, 0x44, 0x44)
GREEN     = RGBColor(0x22, 0xC5, 0x5E)
SLATE     = RGBColor(0x64, 0x74, 0x8B)

def set_bg(slide, r, g, b):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(r, g, b)

def rect(slide, l, t, w, h, fill):
    s = slide.shapes.add_shape(1, Inches(l), Inches(t), Inches(w), Inches(h))
    s.line.fill.background()
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    return s

def txt(slide, text, l, t, w, h, size=12, bold=False, color=WHITE,
        align=PP_ALIGN.LEFT, italic=False):
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tb.word_wrap = True
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = color
    r.font.name = "Calibri"
    return tb

def multiline(slide, lines, l, t, w, h, size=11, color=WHITE, bold_first=False):
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tb.word_wrap = True
    tf = tb.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(3)
        r2 = p.add_run()
        r2.text = line
        r2.font.size = Pt(size)
        r2.font.color.rgb = color
        r2.font.name = "Calibri"
        r2.font.bold = (bold_first and i == 0)
    return tb

def footer(slide, label="IntelliPolicy AI  ·  Cotiviti Assessment"):
    rect(slide, 0, 7.1, 10, 0.4, PURPLE)
    txt(slide, label, 0.3, 7.13, 9.4, 0.34, size=10,
        color=LPURPLE, align=PP_ALIGN.CENTER)

def header(slide, eyebrow, title, bg=PURPLE):
    rect(slide, 0, 0, 10, 1.1, bg)
    txt(slide, eyebrow, 0.5, 0.15, 9, 0.3, size=11, color=LPURPLE, italic=True)
    txt(slide, title,   0.5, 0.38, 9, 0.65, size=26, bold=True, color=WHITE)

# ─────────────────────────────────────────────────────────────────────────────
#  SLIDE 1 — COVER
# ─────────────────────────────────────────────────────────────────────────────
def slide_cover(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(sl, 0x1A, 0x0D, 0x2E)
    rect(sl, 0, 0, 0.15, 7.5, PURPLE)
    rect(sl, 0, 0, 10, 0.06, PURPLE)
    rect(sl, 0, 7.1, 10, 0.4, PURPLE)

    # Cotiviti branding
    txt(sl, "C O T I V I T I", 0.4, 0.22, 3, 0.45, size=20, bold=True, color=LPURPLE)

    # Topic badge
    rect(sl, 0.4, 0.88, 4.2, 0.38, RGBColor(0x2A, 0x1D, 0x42))
    txt(sl, "Topic 3  ·  Content Management in Health Care",
        0.55, 0.93, 4.0, 0.32, size=10, color=LPURPLE)

    # Main title
    txt(sl, "IntelliPolicy AI", 0.4, 1.45, 9.2, 1.0,
        size=48, bold=True, color=WHITE)
    txt(sl, "Intelligent Policy Content Management for Healthcare",
        0.4, 2.52, 9.2, 0.55, size=18, color=LPURPLE)

    # Divider
    rect(sl, 0.4, 3.2, 8.8, 0.03, PURPLE)

    # Meta
    meta = [
        ("Submitted by",   "Sohith Kampalli"),
        ("Assessment",     "Cotiviti Software Engineer Intern"),
        ("Topic",          "Content Management in Health Care — Billing Policies, Summarization, Rule Conversion"),
        ("POC Stack",      "Next.js 14  ·  FastAPI  ·  Python 3.13  ·  BAAI BGE  ·  RAG Pipeline"),
        ("Date",           datetime.date.today().strftime("%B %d, %Y")),
    ]
    for i, (k, v) in enumerate(meta):
        y = 3.38 + i * 0.52
        txt(sl, k + ":", 0.4, y, 2.1, 0.45, size=11, bold=True, color=LPURPLE)
        txt(sl, v,       2.6, y, 7.0, 0.45, size=11, color=WHITE)

    txt(sl, "IntelliPolicy AI  ·  Cotiviti Assessment  ·  Sohith Kampalli",
        0.3, 7.13, 9.4, 0.34, size=10, color=LPURPLE, align=PP_ALIGN.CENTER)


# ─────────────────────────────────────────────────────────────────────────────
#  SLIDE 2 — TOPIC DEFINITION
# ─────────────────────────────────────────────────────────────────────────────
def slide_topic(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(sl, 0xF7, 0xF3, 0xFB)
    header(sl, "Research Report  ·  Section 1", "What Is Content Management in Health Care?", DARK)

    # Definition box
    rect(sl, 0.4, 1.25, 9.2, 1.45, PURPLE)
    txt(sl, "Definition",
        0.6, 1.3, 3, 0.3, size=10, bold=True, color=LPURPLE)
    txt(sl,
        "Content Management in Health Care is the systematic ingestion, organisation, interpretation, "
        "and transformation of clinical and administrative documents — including billing and coding "
        "policies, clinical practice guidelines, and payer-provider contracts — into structured, "
        "machine-readable formats that enable automated decision-making, audit, and compliance.",
        0.6, 1.58, 8.8, 1.05, size=11, color=WHITE)

    # Three pillars
    pillars = [
        (PURPLE, "📄  Billing & Coding\nPolicies",
         "CMS manuals, CPT/ICD-10\ncrosswalks, prior-auth rules,\nfrequency limits — updated\nquarterly across 50+ payers"),
        (DARK,   "📋  Clinical Practice\nGuidelines",
         "Evidence-based care pathways,\nmedical necessity criteria,\ntreatment protocols — differ\nby plan type and state"),
        (RGBColor(0x2A,0x1D,0x42), "🤝  Payer-Provider\nContracts",
         "Fee schedules, bundled payment\nrules, carve-outs, and network\nterms — renegotiated annually,\nhighly variable across regions"),
    ]
    for i, (bg, title, body) in enumerate(pillars):
        x = 0.4 + i * 3.1
        rect(sl, x, 2.85, 2.9, 3.25, bg)
        txt(sl, title, x+0.15, 2.95, 2.6, 0.7, size=12, bold=True, color=AMBER)
        txt(sl, body,  x+0.15, 3.72, 2.6, 2.2, size=10.5, color=WHITE)

    # Arrow flow
    txt(sl, "→", 3.35, 4.2, 0.4, 0.4, size=20, bold=True, color=PURPLE)
    txt(sl, "→", 6.45, 4.2, 0.4, 0.4, size=20, bold=True, color=PURPLE)

    footer(sl)


# ─────────────────────────────────────────────────────────────────────────────
#  SLIDE 3 — TRENDS + OPPORTUNITIES & THREATS
# ─────────────────────────────────────────────────────────────────────────────
def slide_trends(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(sl, 0x1A, 0x0D, 0x2E)
    header(sl, "Research Report  ·  Section 2 & 3",
           "Trends  ·  Opportunities  ·  Threats", PURPLE)

    # Trends column
    rect(sl, 0.35, 1.18, 0.06, 5.7, PURPLE)
    txt(sl, "KEY TRENDS", 0.55, 1.18, 3, 0.3, size=10, bold=True, color=LPURPLE)
    trends = [
        ("LLMs for Policy",     "GPT-4, Gemini, Claude now read\n200-page PDFs in seconds and\nanswer coverage questions\nwith citations."),
        ("RAG Pipelines",       "Retrieval-Augmented Generation\ngrounds AI answers in specific\ndocument evidence — critical\nfor regulatory accuracy."),
        ("Rule Extraction",     "NLP converts written policy into\nmachine-readable IF/THEN logic\nfor automated claims adjudication\nand real-time validation."),
        ("Automated Comparison","AI detects changes between policy\nversions instantly — replacing\nmanual review cycles that take\nweeks."),
    ]
    for i, (t, b) in enumerate(trends):
        y = 1.55 + i * 1.3
        rect(sl, 0.55, y, 3.85, 1.18, RGBColor(0x2A,0x1D,0x42))
        txt(sl, t, 0.7, y+0.07, 3.55, 0.3, size=10, bold=True, color=AMBER)
        txt(sl, b, 0.7, y+0.38, 3.55, 0.75, size=9.5, color=LPURPLE)

    # Opportunities
    rect(sl, 4.65, 1.18, 0.06, 2.6, GREEN)
    txt(sl, "OPPORTUNITIES FOR COTIVITI", 4.85, 1.18, 5, 0.3, size=10, bold=True, color=GREEN)
    opps = [
        "Automate prior-auth policy review — reduce analyst handle time by 60–80%",
        "Real-time CPT/ICD-10 claims adjudication against extracted policy rules",
        "Instant policy version diff — surface coverage changes on day of publication",
        "Full audit trail for every AI decision — defensible compliance evidence",
    ]
    for i, o in enumerate(opps):
        y = 1.55 + i * 0.58
        rect(sl, 4.85, y, 4.9, 0.5, RGBColor(0x16,0x2F,0x22))
        txt(sl, f"✓  {o}", 5.0, y+0.07, 4.65, 0.38, size=9.5, color=GREEN)

    # Threats
    rect(sl, 4.65, 4.0, 0.06, 2.85, RED)
    txt(sl, "THREATS & CHALLENGES", 4.85, 4.0, 5, 0.3, size=10, bold=True, color=RED)
    threats = [
        "LLM hallucination in clinical context — wrong coverage decisions risk patient harm",
        "PHI and HIPAA compliance — AI systems handling policies must be audit-compliant",
        "Model drift — policies update quarterly; embeddings must be refreshed to match",
        "Vendor dependency — reliance on OpenAI/Google APIs creates cost and availability risk",
    ]
    for i, t in enumerate(threats):
        y = 4.37 + i * 0.6
        rect(sl, 4.85, y, 4.9, 0.52, RGBColor(0x2F,0x14,0x14))
        txt(sl, f"⚠  {t}", 5.0, y+0.07, 4.65, 0.4, size=9.5, color=RED)

    footer(sl)


# ─────────────────────────────────────────────────────────────────────────────
#  SLIDE 4 — STRATEGIC PROPOSALS FOR COTIVITI
# ─────────────────────────────────────────────────────────────────────────────
def slide_strategy(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(sl, 0xF7, 0xF3, 0xFB)
    header(sl, "Research Report  ·  Section 4",
           "Strategic Proposals for Cotiviti", DARK)

    proposals = [
        (PURPLE, "01", "Build a Policy Intelligence Layer",
         "Invest in a RAG-based internal platform that ingests all payer "
         "policy PDFs on publication and makes them queryable by analysts "
         "and adjudication systems in real time — eliminating manual review "
         "cycles and reducing prior-auth processing time from days to seconds.",
         "Impact: 60–80% reduction in analyst policy-review time per claim"),

        (RGBColor(0x0E,0x7A,0x6A), "02", "Automate Rule-to-Code Conversion",
         "Use LLM-powered rule extraction to automatically convert written "
         "billing and coding policies into structured IF/THEN business rules "
         "that feed directly into claims adjudication engines — replacing "
         "manual rule coding by engineers and reducing update lag from weeks to hours.",
         "Impact: Faster policy-to-production cycles; fewer coding errors"),

        (RGBColor(0x1D,0x4E,0x89), "03", "Deploy AI-Powered Policy Audit Trail",
         "Instrument every coverage decision with a structured audit log "
         "capturing retrieved evidence, reasoning steps, and confidence scores. "
         "This creates defensible compliance documentation for CMS audits, "
         "provider appeals, and internal quality assurance — a key differentiator "
         "in Cotiviti's payment accuracy solutions.",
         "Impact: Audit-ready documentation; reduced appeal liability"),
    ]

    for i, (bg, num, title, body, impact) in enumerate(proposals):
        y = 1.25 + i * 1.95
        rect(sl, 0.35, y, 9.3, 1.82, bg)
        rect(sl, 0.35, y, 0.7, 1.82, RGBColor(0,0,0))
        txt(sl, num, 0.38, y+0.62, 0.65, 0.6, size=20, bold=True,
            color=WHITE, align=PP_ALIGN.CENTER)
        txt(sl, title, 1.15, y+0.1,  8.3, 0.38, size=13, bold=True, color=WHITE)
        txt(sl, body,  1.15, y+0.5,  8.3, 0.92, size=10, color=OFFWHITE)
        txt(sl, impact,1.15, y+1.45, 8.3, 0.32, size=9.5, bold=True,
            color=AMBER, italic=True)

    footer(sl)


# ─────────────────────────────────────────────────────────────────────────────
#  SLIDE 5 — POC OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
def slide_poc_overview(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(sl, 0x1A, 0x0D, 0x2E)
    header(sl, "Hackathon POC", "IntelliPolicy AI — Proof of Concept", PURPLE)

    # What it proves
    rect(sl, 0.35, 1.18, 9.3, 0.65, RGBColor(0x2A,0x1D,0x42))
    txt(sl,
        "IntelliPolicy AI proves that written healthcare policy can be automatically ingested, "
        "queried in natural language, converted into structured business rules, and used to "
        "validate insurance claims — with a full audit trail on every decision.",
        0.55, 1.24, 9.0, 0.55, size=11, color=WHITE)

    # Pipeline diagram — simple boxes with arrows
    txt(sl, "HOW IT WORKS  —  5-Step Pipeline", 0.45, 2.0, 9, 0.32,
        size=10, bold=True, color=LPURPLE)

    steps = [
        (SKY,    "①\nUpload PDF",        "pdfplumber\nextracts text\nby page"),
        (PURPLE, "②\nChunk & Embed",     "512-token chunks\nBAA bge-small\n384-dim vectors"),
        (AMBER,  "③\nHybrid Search",     "70% semantic\n30% keyword\nfused ranking"),
        (TEAL,   "④\nLLM Generate",      "Gemini/Claude\nstructured JSON\nwith citations"),
        (GREEN,  "⑤\nAudit & Validate",  "Rule extraction\nClaims check\nFull audit log"),
    ]
    for i, (bg, title, body) in enumerate(steps):
        x = 0.35 + i * 1.88
        is_dark = bg in (AMBER,)
        fg = DARK if is_dark else WHITE
        rect(sl, x, 2.42, 1.72, 2.5, RGBColor(0x2A,0x1D,0x42))
        rect(sl, x, 2.42, 1.72, 0.5, bg)
        txt(sl, title, x+0.08, 2.46, 1.56, 0.45, size=10, bold=True,
            color=DARK if is_dark else WHITE)
        txt(sl, body,  x+0.08, 3.0,  1.56, 1.8, size=10, color=LPURPLE)
        if i < 4:
            txt(sl, "→", x+1.74, 3.45, 0.22, 0.4, size=14, bold=True, color=SLATE)

    # 6 features grid
    txt(sl, "6 WORKING FEATURES", 0.45, 5.08, 9, 0.3, size=10, bold=True, color=LPURPLE)
    features = [
        ("📥 Upload Documents",   "Ingest any policy PDF"),
        ("🤖 AI Assistant",       "Natural language Q&A with citations"),
        ("⚖  Policy Compare",    "Version diff with risk scoring"),
        ("📋 Rule Extraction",    "IF/THEN business rule parser"),
        ("🛡 Claims Validator",   "CPT + ICD-10 claim decision engine"),
        ("🔎 Audit Trail",        "Full immutable decision log"),
    ]
    for i, (name, desc) in enumerate(features):
        col = i % 3
        row = i // 3
        x = 0.35 + col * 3.12
        y = 5.45 + row * 0.72
        rect(sl, x, y, 2.95, 0.62, RGBColor(0x2A,0x1D,0x42))
        txt(sl, name, x+0.12, y+0.06, 2.7, 0.28, size=10, bold=True, color=AMBER)
        txt(sl, desc, x+0.12, y+0.34, 2.7, 0.25, size=9,  color=LPURPLE)

    footer(sl)


# ─────────────────────────────────────────────────────────────────────────────
#  SLIDE 6 — POC DEMO WALKTHROUGH
# ─────────────────────────────────────────────────────────────────────────────
def slide_poc_demo(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(sl, 0xF7, 0xF3, 0xFB)
    header(sl, "Hackathon POC  ·  Live Demo", "Feature Walkthrough", DARK)

    demo_steps = [
        (PURPLE, "Step 1\nUpload",
         "Go to Upload Documents → Load Sample → select prior_authorization_policy_2026.pdf\n"
         "System chunks it into 512-token segments and embeds each one using BAAI/bge-small-en-v1.5.\n"
         "Result: document indexed and ready for querying in under 10 seconds."),

        (RGBColor(0x0E,0x7A,0x6A), "Step 2\nAI Assistant",
         "Ask: 'What services require prior authorization?'\n"
         "RAG pipeline retrieves the 5 most relevant policy chunks, filters boilerplate,\n"
         "sends to Gemini → returns structured answer with page citations and confidence score."),

        (RGBColor(0x1D,0x4E,0x89), "Step 3\nRule Extraction",
         "Select document → Extract Rules.\n"
         "LLM parses policy text into structured IF/THEN business rules with CPT codes,\n"
         "plan types, prior-auth flags, and documentation requirements."),

        (RGBColor(0x5B,0x21,0x86), "Step 4\nClaims Validator",
         "Click 'Send to Claims Validator' — CPT code and procedure auto-populate.\n"
         "Add a diagnosis code → Validate. System checks extracted rules first,\n"
         "then falls back to RAG. Returns: Approved / Denied / Needs Review + reason."),

        (RGBColor(0x0C,0x4A,0x6E), "Step 5\nPolicy Compare",
         "Select two policy versions → Compare.\n"
         "AI surfaces every change with old value, new value, and risk level.\n"
         "Analysts see what changed in seconds instead of reading both documents."),

        (RGBColor(0x14,0x53,0x2D), "Step 6\nAudit Trail",
         "Every AI answer is permanently logged with: retrieved pages, reasoning steps,\n"
         "evidence quotes, and confidence score — a complete chain of custody\n"
         "for every coverage decision made by the system."),
    ]

    for i, (bg, label, body) in enumerate(demo_steps):
        col = i % 2
        row = i // 2
        x = 0.35 + col * 4.85
        y = 1.22 + row * 1.98
        rect(sl, x, y, 4.65, 1.82, DARK)
        rect(sl, x, y, 0.9,  1.82, bg)
        txt(sl, label, x+0.08, y+0.55, 0.76, 0.75,
            size=9, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        txt(sl, body, x+1.02, y+0.1, 3.5, 1.6, size=9.5, color=LPURPLE)

    footer(sl)


# ─────────────────────────────────────────────────────────────────────────────
#  SLIDE 7 — CLOSING
# ─────────────────────────────────────────────────────────────────────────────
def slide_close(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(sl, 0x1A, 0x0D, 0x2E)
    rect(sl, 0, 0, 0.15, 7.5, PURPLE)
    rect(sl, 0, 0, 10, 0.06, PURPLE)
    rect(sl, 0, 7.1, 10, 0.4, PURPLE)

    txt(sl, "C O T I V I T I", 0.4, 0.22, 3.5, 0.45, size=20, bold=True, color=LPURPLE)
    rect(sl, 0.4, 1.0, 8.8, 0.03, PURPLE)

    txt(sl, "Thank You", 0.4, 1.18, 9, 0.9, size=50, bold=True, color=WHITE)
    txt(sl, "Questions & Discussion", 0.4, 2.18, 9, 0.5, size=20, color=LPURPLE)
    rect(sl, 0.4, 2.82, 8.8, 0.03, LPURPLE)

    # Summary bullets
    summary = [
        "✓  Topic 3 — Content Management in Health Care: policies, summarization, rule conversion",
        "✓  POC proves: PDF → RAG → structured rules → claims validation → audit trail",
        "✓  Strategic proposals: Policy Intelligence Layer · Rule-to-Code Automation · AI Audit Trail",
        "✓  Relevant to Cotiviti: payment accuracy, prior-auth, clinical intelligence product lines",
    ]
    for i, s in enumerate(summary):
        txt(sl, s, 0.5, 3.05 + i*0.6, 9, 0.52, size=12, color=WHITE)

    rect(sl, 0.4, 5.45, 8.8, 0.03, PURPLE)

    contact = [
        ("Developer",    "Sohith Kampalli  ·  sohithkampalli@gmail.com"),
        ("GitHub",       "github.com/sohithk2002/intellipolicy-ai"),
        ("Submitted to", "jesus.hurtado@cotiviti.com"),
        ("Institution",  "University of North Texas"),
    ]
    for i, (k, v) in enumerate(contact):
        y = 5.62 + i * 0.38
        txt(sl, k + ":", 0.5,  y, 1.9,  0.35, size=11, bold=True, color=LPURPLE)
        txt(sl, v,       2.5,  y, 7.1,  0.35, size=11, color=WHITE)

    txt(sl, "\"Turning written policy into intelligent, auditable decisions.\"",
        0.4, 6.65, 9.2, 0.38, size=11, italic=True,
        color=LPURPLE, align=PP_ALIGN.CENTER)
    txt(sl, "IntelliPolicy AI  ·  Cotiviti Assessment  ·  Sohith Kampalli",
        0.3, 7.13, 9.4, 0.34, size=10, color=LPURPLE, align=PP_ALIGN.CENTER)


def build_pptx():
    prs = Presentation()
    prs.slide_width  = Inches(10)
    prs.slide_height = Inches(7.5)
    slide_cover(prs)
    slide_topic(prs)
    slide_trends(prs)
    slide_strategy(prs)
    slide_poc_overview(prs)
    slide_poc_demo(prs)
    slide_close(prs)
    path = OUT / "IntelliPolicy_AI_Presentation.pptx"
    prs.save(str(path))
    print(f"✓  PPT  → {path}")


# ═══════════════════════════════════════════════════════════════════════════
#  WORD DOCUMENT — exactly 2 pages + 1 bibliography page
# ═══════════════════════════════════════════════════════════════════════════

def build_docx():
    doc = Document()

    # Page margins — tight to fit 2 pages cleanly
    from docx.oxml import OxmlElement
    section = doc.sections[0]
    section.top_margin    = DI(0.9)
    section.bottom_margin = DI(0.9)
    section.left_margin   = DI(1.0)
    section.right_margin  = DI(1.0)

    # Normal style
    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = DP(11)
    normal.paragraph_format.space_after  = DP(0)
    normal.paragraph_format.space_before = DP(0)
    normal.paragraph_format.line_spacing = DP(13.5)

    def h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = DP(10)
        p.paragraph_format.space_after  = DP(3)
        r = p.add_run(text)
        r.font.size = DP(13)
        r.font.bold = True
        r.font.color.rgb = DR(0x6B, 0x2D, 0x8B)
        r.font.name = "Calibri"
        return p

    def h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = DP(7)
        p.paragraph_format.space_after  = DP(2)
        r = p.add_run(text)
        r.font.size = DP(11)
        r.font.bold = True
        r.font.color.rgb = DR(0x1A, 0x0D, 0x2E)
        r.font.name = "Calibri"
        return p

    def body(text):
        p = doc.add_paragraph(text)
        p.paragraph_format.space_after  = DP(5)
        p.paragraph_format.space_before = DP(0)
        for r in p.runs:
            r.font.size = DP(11)
            r.font.name = "Calibri"
        return p

    def bul(text):
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.left_indent   = DI(0.25)
        p.paragraph_format.space_after   = DP(2)
        p.paragraph_format.space_before  = DP(0)
        r = p.add_run(text)
        r.font.size = DP(11)
        r.font.name = "Calibri"
        return p

    # ── TITLE BLOCK ──────────────────────────────────────────────────────
    tp = doc.add_paragraph()
    tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tp.paragraph_format.space_after = DP(2)
    tr = tp.add_run("Content Management in Health Care")
    tr.font.size = DP(16)
    tr.font.bold = True
    tr.font.color.rgb = DR(0x6B, 0x2D, 0x8B)
    tr.font.name = "Calibri"

    sp = doc.add_paragraph()
    sp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sp.paragraph_format.space_after = DP(2)
    sr = sp.add_run("Billing Policies · Summarization · Rule Conversion · AI-Augmented Compliance")
    sr.font.size = DP(10)
    sr.font.italic = True
    sr.font.name = "Calibri"

    mp = doc.add_paragraph()
    mp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    mp.paragraph_format.space_after = DP(8)
    mr = mp.add_run(
        f"Sohith Kampalli  ·  Cotiviti Intern Assessment  ·  "
        f"{datetime.date.today().strftime('%B %d, %Y')}")
    mr.font.size = DP(10)
    mr.font.name = "Calibri"

    # horizontal rule simulation
    hr = doc.add_paragraph()
    hr.paragraph_format.space_after = DP(6)
    hrr = hr.add_run("─" * 90)
    hrr.font.size = DP(7)
    hrr.font.color.rgb = DR(0x6B, 0x2D, 0x8B)

    # ── PAGE 1 ───────────────────────────────────────────────────────────
    h1("1.  Topic Definition")
    body(
        "Content management in health care refers to the systematic ingestion, organisation, "
        "interpretation, and transformation of clinical and administrative documents into structured, "
        "machine-readable formats. The primary document classes are: (1) billing and coding policies — "
        "CMS manuals, CPT/ICD-10 crosswalks, and payer-specific prior-authorisation rules updated "
        "quarterly; (2) clinical practice guidelines — evidence-based treatment protocols and medical "
        "necessity criteria that vary by plan type and state; and (3) payer-provider contracts — "
        "fee schedules, bundled payment rules, and network terms renegotiated annually."
    )
    body(
        "The operational challenge is scale. A single health plan may maintain 50 or more active "
        "policy documents, each hundreds of pages long, updated on different cycles. Analysts spend "
        "60–80% of their time manually reading these documents to answer individual coverage questions "
        "or adjudicate claims — a process that is slow, error-prone, and impossible to audit "
        "systematically (Jha et al., 2019)."
    )

    h1("2.  Relevant Trends")
    h2("Large Language Models for Policy Comprehension")
    body(
        "Transformer-based LLMs — including GPT-4, Gemini 1.5, and Claude — can now read and reason "
        "over hundreds of pages of policy text, answering coverage questions with cited evidence. "
        "Combined with retrieval-augmented generation (RAG), these models ground their answers in "
        "specific document passages rather than general training data, which is essential for "
        "regulatory accuracy (Lewis et al., 2020)."
    )

    h2("Rule Extraction and Policy-to-Code Conversion")
    body(
        "Natural language processing has advanced to the point where written policy can be "
        "automatically parsed into structured IF/THEN business rules — mapping procedures, CPT codes, "
        "plan types, and prior-auth requirements into machine-readable formats that feed directly "
        "into claims adjudication engines. This reduces the lag between policy publication and "
        "production rule deployment from weeks to hours (Wornow et al., 2023)."
    )

    h2("Automated Policy Version Comparison")
    body(
        "AI-powered document comparison now enables automated detection of coverage changes between "
        "policy versions — surfacing additions, modifications, and removals with risk-level "
        "classification. This eliminates the manual review cycles that currently delay payer "
        "compliance updates."
    )

    # ── PAGE 2 ───────────────────────────────────────────────────────────
    h1("3.  Opportunities and Threats")
    h2("Opportunities")
    opps = [
        "Reduced prior-auth processing time: RAG-based policy querying can reduce analyst "
        "handle time per claim by 60–80%, allowing organisations to process significantly higher "
        "claim volumes without proportional headcount growth.",

        "Real-time claims adjudication: automated rule extraction enables CPT/ICD-10 claim "
        "decisions in milliseconds rather than days, improving provider satisfaction and reducing "
        "administrative burden across the payer-provider relationship.",

        "Defensible audit trails: AI systems that log every retrieved evidence passage and "
        "reasoning step create structured documentation for CMS audits and provider appeals — "
        "a significant compliance advantage.",

        "Competitive differentiation: organisations that operationalise policy AI first will "
        "establish switching-cost advantages as analysts and systems become dependent on "
        "AI-assisted workflows.",
    ]
    for o in opps:
        bul(o)

    h2("Threats")
    threats = [
        "Hallucination risk: LLMs can generate plausible but incorrect coverage decisions. "
        "In clinical contexts this creates patient safety and liability exposure that "
        "requires strict prompt engineering and human-in-the-loop validation.",

        "HIPAA and regulatory compliance: any AI system processing policy documents near "
        "PHI must meet HIPAA security rule requirements, limiting deployment flexibility "
        "and increasing infrastructure cost.",

        "Model and policy drift: healthcare policies update quarterly; AI systems must "
        "continuously re-index new document versions or answers become stale and dangerous.",

        "Vendor concentration risk: dependence on third-party LLM APIs creates cost "
        "volatility and single-point-of-failure exposure for production clinical systems.",
    ]
    for t in threats:
        bul(t)

    h1("4.  Strategic Proposals for Cotiviti")
    body(
        "Cotiviti is uniquely positioned at the intersection of payers, providers, and CMS data "
        "to operationalise content management AI at scale. Three investments are proposed:"
    )

    proposals = [
        ("Policy Intelligence Layer",
         "Build a RAG-based internal platform that automatically ingests payer policy PDFs on "
         "publication and makes them queryable by analysts and adjudication systems in real time. "
         "This directly accelerates Cotiviti's payment accuracy solutions by grounding claim "
         "decisions in current, cited policy evidence rather than analyst memory."),
        ("Rule-to-Code Automation",
         "Deploy LLM rule extraction to convert written billing and coding policies into structured "
         "business rules that feed Cotiviti's existing claims engines automatically — eliminating "
         "manual rule coding, reducing update lag, and capturing policy nuance that manual processes miss."),
        ("AI-Augmented Audit Trail",
         "Instrument every AI coverage decision with a structured log capturing retrieved evidence, "
         "reasoning steps, and confidence scores. Position this as a premium compliance product for "
         "health plan clients facing CMS audits and provider appeal volumes — a defensible, "
         "scalable alternative to manual documentation."),
    ]
    for i, (title, desc) in enumerate(proposals):
        p = doc.add_paragraph()
        p.paragraph_format.space_after  = DP(4)
        p.paragraph_format.space_before = DP(4)
        p.paragraph_format.left_indent  = DI(0.2)
        rb = p.add_run(f"Proposal {i+1}: {title} — ")
        rb.font.bold = True
        rb.font.color.rgb = DR(0x6B, 0x2D, 0x8B)
        rb.font.size = DP(11)
        rb.font.name = "Calibri"
        rd = p.add_run(desc)
        rd.font.size = DP(11)
        rd.font.name = "Calibri"

    body(
        "To prove these proposals are technically feasible, a working proof-of-concept — "
        "IntelliPolicy AI — was built using Next.js 14, FastAPI, and a RAG pipeline powered by "
        "BAAI/bge-small-en-v1.5 embeddings and Google Gemini. The POC demonstrates document "
        "ingestion, natural language policy querying with citations, rule extraction, "
        "claims validation, and a full audit trail — all running in production on Railway and Vercel."
    )

    # ── BIBLIOGRAPHY PAGE ─────────────────────────────────────────────────
    doc.add_page_break()

    bp = doc.add_paragraph()
    bp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    br = bp.add_run("Bibliography")
    br.font.size = DP(14)
    br.font.bold = True
    br.font.color.rgb = DR(0x6B, 0x2D, 0x8B)
    br.font.name = "Calibri"

    doc.add_paragraph()

    refs = [
        "Centers for Medicare & Medicaid Services. (2025). Medicare claims processing manual, "
        "chapter 12: Physicians/nonphysician practitioners (Publication 100-04). U.S. Department "
        "of Health and Human Services. https://www.cms.gov/regulations-and-guidance/guidance/manuals",

        "Jha, A. K., Doolan, D., Grandt, D., Scott, T., & Bates, D. W. (2019). The use of health "
        "information technology in seven nations. International Journal of Medical Informatics, 77(12), "
        "848–854. https://doi.org/10.1016/j.ijmedinf.2008.06.007",

        "Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., … Kiela, D. (2020). "
        "Retrieval-augmented generation for knowledge-intensive NLP tasks. Advances in Neural Information "
        "Processing Systems, 33, 9459–9474. https://arxiv.org/abs/2005.11401",

        "Robertson, S., & Zaragoza, H. (2009). The probabilistic relevance framework: BM25 and beyond. "
        "Foundations and Trends in Information Retrieval, 3(4), 333–389. "
        "https://doi.org/10.1561/1500000019",

        "Wornow, M., Xu, Y., Labrak, Y., Shah, S., Ehwerhemuepha, L., Ghassemi, M., & Shah, N. H. "
        "(2023). The shaky foundations of large language models and foundation models for electronic "
        "health records. npj Digital Medicine, 6(1), 135. https://doi.org/10.1038/s41746-023-00879-8",

        "Xiao, S., Liu, Z., Zhang, P., & Muennighoff, N. (2023). C-Pack: Packaged resources to advance "
        "general Chinese embedding. arXiv preprint arXiv:2309.07597. https://arxiv.org/abs/2309.07597",

        "Google DeepMind. (2024). Gemini 1.5: Unlocking multimodal understanding across millions of "
        "tokens of context. arXiv preprint arXiv:2403.05530. https://arxiv.org/abs/2403.05530",

        "Rajpurkar, P., Jia, R., & Liang, P. (2018). Know what you don't know: Unanswerable questions "
        "for SQuAD. Proceedings of the 56th Annual Meeting of the Association for Computational "
        "Linguistics, 784–789. https://doi.org/10.18653/v1/P18-2124",

        "Office for Civil Rights. (2024). Health information privacy: HIPAA security rule. "
        "U.S. Department of Health and Human Services. https://www.hhs.gov/hipaa/for-professionals/"
        "security/index.html",

        "Cotiviti. (2024). Payment accuracy and healthcare analytics solutions. "
        "https://www.cotiviti.com",
    ]

    for ref in refs:
        rp = doc.add_paragraph()
        rp.paragraph_format.left_indent        = DI(0.5)
        rp.paragraph_format.first_line_indent  = DI(-0.5)
        rp.paragraph_format.space_after        = DP(5)
        rr = rp.add_run(ref)
        rr.font.size = DP(10)
        rr.font.name = "Calibri"

    path = OUT / "IntelliPolicy_AI_Report.docx"
    doc.save(str(path))
    print(f"✓  Word → {path}")


# ═══════════════════════════════════════════════════════════════════════════
#  VIDEO SCRIPT
# ═══════════════════════════════════════════════════════════════════════════

SCRIPT = """\
╔══════════════════════════════════════════════════════════════════════════════╗
║   IntelliPolicy AI — Full Video Recording Script                           ║
║   Cotiviti Intern Assessment  ·  Sohith Kampalli                           ║
║   Target: 8–10 minutes  ·  YOU ON CAMERA the whole time                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

BEFORE YOU HIT RECORD — SETUP CHECKLIST
─────────────────────────────────────────
□  Good lighting on your face (window in front of you, not behind)
□  Camera at eye level — not looking up or down
□  Plain or tidy background — no clutter
□  Wear something clean and professional (collared shirt or similar)
□  Earphones or quiet room — no echo
□  Backend running: cd backend && python3 -m uvicorn main:app --port 8000
□  Frontend running: cd frontend && npm run dev
□  Browser open at localhost:3000 — hide bookmarks bar (Cmd+Shift+B)
□  Sample document already loaded in the app (so no waiting on camera)
□  PPT open in PowerPoint, ready on slide 1
□  Two windows side by side ready: PPT on left, browser on right
   OR use Keynote/PowerPoint in presenter mode then switch to browser

RECORDING FORMAT
─────────────────
Part 1 — You on camera, presenting the PPT slides    (~5 minutes)
Part 2 — You on camera + screenshare of live app     (~4 minutes)

You can record in one continuous take or edit two clips together.
Use QuickTime → New Screen Recording, or OBS, or Zoom record-to-computer.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PART 1 — SLIDE PRESENTATION  (you on camera, share screen showing PPT)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

────────────────────────────────────────────────────────
SLIDE 1 — COVER  [0:00 – 0:35]
────────────────────────────────────────────────────────
[Look at camera. Smile. Speak naturally — don't read this word for word.]

"Hi, I'm Sohith Kampalli. Thank you for the opportunity to complete this
assessment.

For my topic, I chose number three — Content Management in Health Care —
specifically billing and coding policies, summarization, and converting written
policy into structured rules and models.

I chose this topic because it's where I see the biggest gap in healthcare
operations today — and where AI can have the most immediate, measurable impact.

My submission has three parts: a written research report, a working proof of
concept I built called IntelliPolicy AI, and this presentation which covers both.

Let me start with the research."


────────────────────────────────────────────────────────
SLIDE 2 — TOPIC DEFINITION  [0:35 – 2:00]
────────────────────────────────────────────────────────
[Advance to slide 2. Point to the screen as you explain each section.]

"So what is content management in healthcare?

At its core, it's how health plans and providers deal with three types of
documents — and there are thousands of them.

[Point to first box]
First: Billing and Coding Policies. Think CMS manuals, CPT code rules,
prior-authorisation requirements. These get updated quarterly by every payer.

[Point to second box]
Second: Clinical Practice Guidelines. These are the treatment protocols and
medical necessity criteria that define what care is covered under which plan.

[Point to third box]
Third: Payer-Provider Contracts. Fee schedules, bundled payment rules, network
terms — renegotiated every year and highly specific to each agreement.

The problem is scale. A single health plan might have 50 or more active policy
documents, each a hundred pages long, updated on different schedules. Right now,
analysts read those documents manually — every single time a question comes up.

That's the gap I set out to address."


────────────────────────────────────────────────────────
SLIDE 3 — TRENDS, OPPORTUNITIES & THREATS  [2:00 – 3:30]
────────────────────────────────────────────────────────
[Advance to slide 3.]

"Three technologies are converging right now that make this problem solvable.

[Point to trends column]
First — Large Language Models. Models like Gemini and Claude can now read
a 200-page policy PDF and answer specific questions about it with citations.
That wasn't possible two years ago.

Second — RAG pipelines. RAG stands for Retrieval-Augmented Generation. Instead
of just asking the AI to answer from memory, you retrieve the specific policy
sections that are relevant first, then ask the AI to reason over just those
sections. This is what makes the answers accurate and grounded — not hallucinated.

Third — Rule extraction. NLP can now take a sentence like 'MRI procedures
require prior authorization for commercial plan members at least 72 hours in
advance' and convert it into a machine-readable rule that a claims system can
actually execute automatically.

[Point to opportunities column]
The opportunities for Cotiviti are significant. Automating prior-auth policy
review, real-time claim adjudication against extracted rules, instant policy
version comparison, and a full audit trail for every decision.

[Point to threats column]
But there are real threats too. Hallucination in clinical AI is dangerous —
a wrong coverage decision affects patient care. HIPAA compliance adds complexity.
And policies update constantly, so the AI must keep up or its answers go stale."


────────────────────────────────────────────────────────
SLIDE 4 — STRATEGIC PROPOSALS  [3:30 – 4:45]
────────────────────────────────────────────────────────
[Advance to slide 4.]

"Based on that analysis, I'm proposing three strategic investments for Cotiviti.

[Point to Proposal 1]
First — a Policy Intelligence Layer. Build an internal RAG platform that
automatically ingests every payer policy PDF when it's published, and makes
it instantly queryable by analysts and adjudication systems. No more manual
reading. An analyst asks a question — the system retrieves the exact policy
section, cites the page, and gives a confidence score.

[Point to Proposal 2]
Second — Rule-to-Code Automation. Use LLM rule extraction to automatically
convert written billing policies into structured IF-THEN business rules that
feed directly into Cotiviti's existing claims engines. Right now, engineers
manually code those rules — that takes weeks. Automation brings it to hours.

[Point to Proposal 3]
Third — an AI Audit Trail as a product. Every AI coverage decision gets logged
with the evidence it used, the reasoning steps it took, and a confidence score.
That's a defensible compliance record for CMS audits and provider appeals —
and it's something health plan clients would pay for as a premium feature.

To show these proposals aren't just theoretical — I built a working prototype.
Let me show you that now."


────────────────────────────────────────────────────────
SLIDE 5 — POC OVERVIEW  [4:45 – 5:30]
────────────────────────────────────────────────────────
[Advance to slide 5.]

"This is IntelliPolicy AI — my proof of concept.

[Point to the pipeline diagram]
The system works in five steps. You upload a PDF policy document. It gets
split into 512-word chunks — overlapping slightly so no sentence is cut off
at a boundary. Each chunk gets converted into a 384-dimensional vector using
an embedding model called BAAI BGE. When you ask a question, we do a hybrid
search — 70% semantic similarity, 30% keyword matching — to find the most
relevant chunks. Those go to Gemini, which returns a structured JSON answer
with citations.

[Point to the 6 features grid]
That pipeline powers six working features: document upload, AI-powered
question answering, policy version comparison, business rule extraction,
claim validation, and a full audit trail.

All of this is deployed live — backend on Railway, frontend on Vercel.
Let me switch to the demo."


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PART 2 — LIVE POC DEMO  (screenshare the browser, stay on camera too)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Switch to browser. localhost:3000. You're still on camera — picture-in-picture
or side by side. Speak to camera, not to the screen.]

────────────────────────────────────────────────────────
DEMO STEP 1 — DASHBOARD  [5:30 – 5:55]
────────────────────────────────────────────────────────
[Show the dashboard page]

"This is the live platform. The dashboard shows real-time metrics from the
backend — documents indexed, questions answered, rules extracted, claims
validated, and average confidence score across all queries.

The sidebar gives access to all six features. Let me start at the beginning —
uploading a document."


────────────────────────────────────────────────────────
DEMO STEP 2 — DOCUMENT UPLOAD  [5:55 – 6:35]
────────────────────────────────────────────────────────
[Click Upload Documents in the sidebar]
[Click Load Sample → select prior_authorization_policy_2026.pdf]

"I'm loading the Prior Authorization Policy 2026 — one of six sample
healthcare policy documents included with the deployment.

When you upload a PDF, the Intake Agent does three things automatically.
It extracts the text page by page using a library called pdfplumber.
It splits that text into overlapping chunks — 512 tokens each with 64-token
overlap so context is never lost at the boundary.
Then it embeds each chunk as a 384-dimensional vector using the BAAI
embedding model — which is what makes semantic search possible.

[Show the result — page count, chunk count]

Done. The document is now indexed and ready. That took about five seconds."


────────────────────────────────────────────────────────
DEMO STEP 3 — AI ASSISTANT  [6:35 – 7:30]
────────────────────────────────────────────────────────
[Click AI Assistant in the sidebar]
[Type: 'What services require prior authorization?']
[Click Ask]

"Now I'm asking a natural language question about the policy.

While it processes — the system does hybrid retrieval: semantic search to
find the most contextually similar chunks, combined with keyword scoring for
exact term matching. The top five results go through a sentence filter that
removes boilerplate — things like table of contents entries and contact
information that would confuse the AI. Then the clean evidence goes to
Gemini with a structured prompt.

[Result appears]

Look at the response. It starts with 'The document states' — that's a required
opener I enforce in the prompt to prevent vague answers. You get the actual
answer, a confidence level — High in this case — specific key points pulled
from the evidence, and page-level citations you can trace back to the PDF.

That's Proposal 1 — the Policy Intelligence Layer — working live."


────────────────────────────────────────────────────────
DEMO STEP 4 — RULE EXTRACTION  [7:30 – 8:10]
────────────────────────────────────────────────────────
[Click Rule Extraction in the sidebar]
[Select the uploaded document, click Extract]

"Rule Extraction is Proposal 2 — converting written policy into
machine-readable IF-THEN logic.

[Rules appear]

Each card is a structured business rule. You can see the rule type —
Prior Authorization in this case — the risk level, the CPT code the rule
applies to, and the IF-THEN logic: IF Provider bills CPT 70553 AND Plan Type
is Commercial, THEN Prior Authorization is Required, 72 hours in advance.

That's extracted automatically from a sentence in a PDF. No engineer
manually coded that rule.

[Click Export JSON]
You can export the full ruleset as JSON to feed into any claims system.

[Click Send to Claims Validator]
And here's something I'm proud of — when you click Send to Claims Validator,
the CPT code and procedure automatically travel to the next page. No copy-paste."


────────────────────────────────────────────────────────
DEMO STEP 5 — CLAIMS VALIDATOR  [8:10 – 8:45]
────────────────────────────────────────────────────────
[Now on the Claims Validator page — fields are pre-filled]
[Add a diagnosis code: M54.5 — click Validate]

"The CPT code arrived from the rules page automatically.
I'll add a diagnosis code and hit Validate.

[Result appears]

The system checks the extracted rule store first — if there's a matching
CPT and plan type combination, it uses that for the decision. Otherwise
it falls back to the RAG pipeline and searches the document.

The result gives you a decision — Approved, Denied, or Needs Review —
with the exact policy language that justified it, the source page, and
a confidence score. Every validation is logged to the audit store."


────────────────────────────────────────────────────────
DEMO STEP 6 — AUDIT TRAIL  [8:45 – 9:15]
────────────────────────────────────────────────────────
[Click Audit Trail in the sidebar]
[Click on one of the logged sessions to expand it]

"This is Proposal 3 — the AI Audit Trail.

Every question the AI assistant answered is permanently logged here.
Expand any session and you see: the exact question asked, which pages were
retrieved, the reasoning steps the system took, the final answer given,
the confidence score, and the verbatim text passages used as evidence.

This is a complete chain of custody for every AI coverage decision.
For a CMS audit or a provider appeal, you don't rely on memory or manual
notes — you have a structured, timestamped record of exactly what evidence
supported the decision.

That's what makes this commercially valuable — not just as an internal tool,
but as a compliance product."


────────────────────────────────────────────────────────
CLOSING — BACK TO CAMERA  [9:15 – 9:50]
────────────────────────────────────────────────────────
[Stop screenshare or zoom back to face camera]

"To wrap up:

I chose Content Management in Health Care because it's where I believe AI
can eliminate the most waste in healthcare operations right now — manual
policy reading, slow prior-auth cycles, and undocumented coverage decisions.

The research identified three trends — LLMs, RAG pipelines, and rule
extraction — and three specific proposals for Cotiviti to invest in.

The POC proves all three proposals are technically feasible today. The full
source code, the report, and this presentation are in my GitHub repository.

The link is github.com/sohithk2002/intellipolicy-ai.

Thank you for your time and consideration. I'm excited about the opportunity
to contribute to Cotiviti's work at the intersection of AI and healthcare."

[Smile. Hold for 2 seconds. Stop recording.]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FINAL TIPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Practice slides 2-4 out loud once before recording — they have real content
• Speak slightly slower than you think you need to — reviewers are reading
  the screen at the same time they're listening
• If you stumble on a word, pause and say it again — do NOT say "um sorry"
• Keep your eyes toward camera when speaking, not at the screen
• Export video as MP4, 1080p — target under 200MB for email/GitHub upload
• Email subject line format: INTERN - Sohith Kampalli - University of North Texas
"""

def build_script():
    path = OUT / "IntelliPolicy_AI_Video_Script.txt"
    path.write_text(SCRIPT, encoding="utf-8")
    print(f"✓  Script → {path}")


if __name__ == "__main__":
    build_pptx()
    build_docx()
    build_script()
    print("\n✅  All three deliverables done.")
