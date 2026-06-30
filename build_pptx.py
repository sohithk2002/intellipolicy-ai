"""
Rebuild PPT using the exact IntelliPolicy AI website colour palette.

Website palette (from globals.css + page.tsx):
  DARK      #111827  — near-black, primary background and headings
  SLATE     #94a3b8  — muted text / secondary elements
  SLATE_D   #64748b  — tertiary / labels
  BODY      #374151  — body text on light slides
  EMERALD   #34d399  — success, live, Rule Extraction accent
  EMERALD_D #10b981  — checkmarks, green states
  AMBER     #fbbf24  — audit, warnings, Claims Validation accent
  CORAL     #f87171  — threats / Audit Trail accent
  WHITE     #ffffff
  LIGHT     #f9fafb  — slide background for light slides
  BORDER    #e5e7eb  — card borders on light slides
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import datetime, pathlib

OUT = pathlib.Path("/Users/sohithkampalli/cotivity/intellipolicy-ai")

# ── exact palette from the website ───────────────────────────────────────────
DARK     = RGBColor(0x11, 0x18, 0x27)   # #111827  near-black
DARK2    = RGBColor(0x1F, 0x29, 0x37)   # card bg on dark slides
DARK3    = RGBColor(0x2D, 0x3A, 0x4A)   # lighter card on dark
SLATE    = RGBColor(0x94, 0xA3, 0xB8)   # muted / secondary
SLATE_D  = RGBColor(0x64, 0x74, 0x8B)   # labels / tertiary
BODY     = RGBColor(0x37, 0x41, 0x51)   # body text on light
BORDER   = RGBColor(0xE5, 0xE7, 0xEB)   # card borders light
LIGHT    = RGBColor(0xF9, 0xFA, 0xFB)   # light slide bg
WHITE    = RGBColor(0xFF, 0xFF, 0xFF)
EMERALD  = RGBColor(0x34, 0xD3, 0x99)   # #34d399  primary green
EMRLD_D  = RGBColor(0x10, 0xB9, 0x81)   # #10b981  darker green
AMBER    = RGBColor(0xFB, 0xBF, 0x24)   # #fbbf24  amber
CORAL    = RGBColor(0xF8, 0x71, 0x71)   # #f87171  coral red
GRAY300  = RGBColor(0xD1, 0xD5, 0xDB)   # gray-300

# feature accent colours — same as used in app
F_UPLOAD  = DARK
F_QA      = SLATE
F_COMPARE = SLATE
F_RULES   = EMERALD
F_CLAIMS  = AMBER
F_AUDIT   = CORAL

# ── helpers ───────────────────────────────────────────────────────────────────
def set_bg(slide, rgb: RGBColor):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = rgb

def rect(slide, l, t, w, h, fill: RGBColor, alpha=None):
    s = slide.shapes.add_shape(1, Inches(l), Inches(t), Inches(w), Inches(h))
    s.line.fill.background()
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    return s

def txt(slide, text, l, t, w, h, size=11, bold=False, color=WHITE,
        align=PP_ALIGN.LEFT, italic=False, wrap=True):
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tb.word_wrap = wrap
    tf = tb.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.size  = Pt(size)
    r.font.bold  = bold
    r.font.italic = italic
    r.font.color.rgb = color
    r.font.name  = "Plus Jakarta Sans"
    return tb

def multiline(slide, lines, l, t, w, h, size=11, color=WHITE, bold_first=False, spacing=3):
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tb.word_wrap = True
    tf = tb.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(spacing)
        r2 = p.add_run()
        r2.text = line
        r2.font.size  = Pt(size)
        r2.font.color.rgb = color
        r2.font.name  = "Plus Jakarta Sans"
        r2.font.bold  = (bold_first and i == 0)
    return tb

def footer_dark(slide, label="IntelliPolicy AI  ·  Cotiviti Assessment  ·  Sohith Kampalli"):
    """Footer for dark slides."""
    rect(slide, 0, 7.13, 10, 0.37, DARK2)
    txt(slide, label, 0.3, 7.17, 9.4, 0.3, size=9,
        color=SLATE_D, align=PP_ALIGN.CENTER)

def footer_light(slide, label="IntelliPolicy AI  ·  Cotiviti Assessment  ·  Sohith Kampalli"):
    """Footer for light slides."""
    rect(slide, 0, 7.13, 10, 0.37, BORDER)
    txt(slide, label, 0.3, 7.17, 9.4, 0.3, size=9,
        color=SLATE_D, align=PP_ALIGN.CENTER)

def header_dark(slide, eyebrow, title):
    rect(slide, 0, 0, 10, 1.08, DARK2)
    txt(slide, eyebrow, 0.5, 0.14, 9, 0.3,
        size=9, bold=True, italic=False, color=SLATE_D,
        align=PP_ALIGN.LEFT)
    # small emerald accent line
    rect(slide, 0.5, 0.44, 0.28, 0.03, EMERALD)
    txt(slide, title, 0.5, 0.5, 9, 0.52,
        size=24, bold=True, color=WHITE)

def header_light(slide, eyebrow, title):
    rect(slide, 0, 0, 10, 1.08, WHITE)
    rect(slide, 0, 1.05, 10, 0.03, BORDER)
    txt(slide, eyebrow, 0.5, 0.14, 9, 0.28,
        size=9, bold=True, color=SLATE_D)
    rect(slide, 0.5, 0.44, 0.28, 0.03, EMERALD)
    txt(slide, title, 0.5, 0.5, 9, 0.52,
        size=24, bold=True, color=DARK)


# ─────────────────────────────────────────────────────────────────────────────
#  SLIDE 1 — COVER  (dark)
# ─────────────────────────────────────────────────────────────────────────────
def slide_cover(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(sl, DARK)

    # left accent bar
    rect(sl, 0, 0, 0.12, 7.5, EMERALD)

    # top eyebrow
    txt(sl, "C O T I V I T I  ·  I N T E R N  A S S E S S M E N T",
        0.32, 0.2, 9.5, 0.38, size=9, bold=True, color=SLATE_D)

    # Topic badge
    rect(sl, 0.32, 0.72, 4.6, 0.36, DARK2)
    rect(sl, 0.32, 0.72, 0.04, 0.36, EMERALD)
    txt(sl, "Topic 3  ·  Content Management in Health Care",
        0.45, 0.77, 4.35, 0.26, size=9.5, bold=True, color=EMERALD)

    # Main title
    txt(sl, "IntelliPolicy AI", 0.32, 1.22, 9.4, 1.0,
        size=54, bold=True, color=WHITE)

    # subtitle
    txt(sl, "Intelligent Policy Content Management for Healthcare",
        0.32, 2.3, 9.4, 0.5, size=16, color=SLATE)

    # thin divider
    rect(sl, 0.32, 3.0, 9.2, 0.02, DARK3)

    # meta grid
    meta = [
        ("Submitted by",  "Sohith Kampalli"),
        ("Assessment",    "Cotiviti Software Engineer Intern — University of North Texas"),
        ("Topic",         "Billing & Coding Policies · Summarization · Rule Conversion"),
        ("Stack",         "Next.js 14  ·  FastAPI  ·  BAAI/bge-small  ·  RAG Pipeline"),
        ("Date",          datetime.date.today().strftime("%B %d, %Y")),
    ]
    for i, (k, v) in enumerate(meta):
        y = 3.18 + i * 0.51
        txt(sl, k + ":", 0.32, y, 2.0, 0.42, size=10, bold=True, color=SLATE_D)
        txt(sl, v,       2.45, y, 7.2, 0.42, size=10, color=WHITE)

    # bottom emerald tag
    rect(sl, 0.32, 6.55, 2.5, 0.38, DARK2)
    rect(sl, 0.32, 6.55, 0.04, 0.38, EMERALD)
    txt(sl, "● LIVE POC  ·  github.com/sohithk2002/intellipolicy-ai",
        0.45, 6.60, 2.35, 0.28, size=8.5, color=EMERALD)

    footer_dark(sl)


# ─────────────────────────────────────────────────────────────────────────────
#  SLIDE 2 — TOPIC DEFINITION  (light)
# ─────────────────────────────────────────────────────────────────────────────
def slide_topic(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(sl, LIGHT)
    header_light(sl, "Research Report  ·  Section 1",
                  "What Is Content Management in Health Care?")

    # Definition card
    rect(sl, 0.4, 1.2, 9.2, 1.4, WHITE)
    rect(sl, 0.4, 1.2, 0.05, 1.4, EMERALD)
    rect(sl, 0.4, 1.2, 9.2, 0.02, BORDER)
    rect(sl, 0.4, 2.58, 9.2, 0.02, BORDER)
    txt(sl, "Definition", 0.6, 1.26, 2, 0.26, size=8.5, bold=True, color=SLATE_D)
    txt(sl,
        "Content Management in Health Care is the systematic ingestion, organisation, interpretation, "
        "and transformation of clinical and administrative documents — including billing and coding "
        "policies, clinical practice guidelines, and payer-provider contracts — into structured, "
        "machine-readable formats enabling automated decision-making, audit, and compliance.",
        0.6, 1.55, 8.85, 0.95, size=11, color=BODY)

    # Three pillars
    pillars = [
        (DARK,   "📄", "Billing & Coding Policies",
         "CMS manuals · CPT/ICD-10 crosswalks\nPrior-auth rules · Frequency limits\nUpdated quarterly by 50+ payers"),
        (BODY,   "📋", "Clinical Practice Guidelines",
         "Evidence-based care pathways\nMedical necessity criteria\nVary by plan type and state"),
        (DARK3,  "🤝", "Payer-Provider Contracts",
         "Fee schedules · Bundled payments\nCarve-outs · Network terms\nRenegotiated annually"),
    ]
    for i, (bg, ico, title, body_text) in enumerate(pillars):
        x = 0.4 + i * 3.1
        rect(sl, x, 2.72, 2.9, 3.3, bg)
        rect(sl, x, 2.72, 2.9, 0.02, EMERALD)
        txt(sl, ico,        x+0.18, 2.83, 0.5, 0.45, size=18)
        txt(sl, title,      x+0.18, 3.35, 2.55, 0.5, size=11.5, bold=True, color=WHITE)
        txt(sl, body_text,  x+0.18, 3.88, 2.55, 1.9, size=10, color=SLATE)

    txt(sl, "→", 3.33, 4.27, 0.35, 0.38, size=16, bold=True, color=SLATE_D)
    txt(sl, "→", 6.43, 4.27, 0.35, 0.38, size=16, bold=True, color=SLATE_D)

    footer_light(sl)


# ─────────────────────────────────────────────────────────────────────────────
#  SLIDE 3 — TRENDS / OPP / THREATS  (dark)
# ─────────────────────────────────────────────────────────────────────────────
def slide_trends(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(sl, DARK)
    header_dark(sl, "Research Report  ·  Sections 2 & 3",
                "Trends  ·  Opportunities  ·  Threats")

    # Trends column header
    rect(sl, 0.35, 1.18, 0.04, 5.8, SLATE_D)
    txt(sl, "KEY TRENDS", 0.55, 1.18, 3.2, 0.28, size=8.5, bold=True, color=SLATE_D)
    trends = [
        ("LLMs for Policy",     "GPT-4, Gemini, Claude read 200-page PDFs\nin seconds and answer coverage questions\nwith page-level citations."),
        ("RAG Pipelines",       "Retrieval-Augmented Generation grounds AI\nanswers in specific document evidence —\ncritical for regulatory accuracy."),
        ("Rule Extraction",     "NLP converts written policy into machine-\nreadable IF/THEN logic for automated\nclaims adjudication."),
        ("Automated Diff",      "AI detects changes between policy versions\ninstantly — replacing manual review\ncycles that take weeks."),
    ]
    for i, (t, b) in enumerate(trends):
        y = 1.55 + i * 1.3
        rect(sl, 0.55, y, 3.75, 1.18, DARK2)
        rect(sl, 0.55, y, 0.04, 1.18, SLATE)
        txt(sl, t, 0.73, y+0.1, 3.45, 0.28, size=10, bold=True, color=WHITE)
        txt(sl, b, 0.73, y+0.42, 3.45, 0.7, size=9.5, color=SLATE)

    # Opportunities column
    rect(sl, 4.55, 1.18, 0.04, 2.75, EMERALD)
    txt(sl, "OPPORTUNITIES", 4.73, 1.18, 5, 0.28, size=8.5, bold=True, color=EMERALD)
    opps = [
        "Automate prior-auth review — 60–80% less analyst handle time",
        "Real-time CPT/ICD-10 adjudication against extracted policy rules",
        "Instant policy version diff — surface coverage changes on publication day",
        "Full audit trail per AI decision — defensible compliance documentation",
    ]
    for i, o in enumerate(opps):
        y = 1.55 + i * 0.6
        rect(sl, 4.73, y, 5.0, 0.5, DARK2)
        rect(sl, 4.73, y, 0.04, 0.5, EMRLD_D)
        txt(sl, f"✓  {o}", 4.88, y+0.09, 4.75, 0.35, size=9.5, color=EMERALD)

    # Threats column
    rect(sl, 4.55, 3.98, 0.04, 3.0, CORAL)
    txt(sl, "THREATS", 4.73, 3.98, 5, 0.28, size=8.5, bold=True, color=CORAL)
    threats = [
        "LLM hallucination in clinical context — wrong decisions risk patient harm",
        "HIPAA compliance — AI systems near PHI must meet security rule requirements",
        "Model drift — policies update quarterly; embeddings must stay current",
        "Vendor dependency — third-party LLM APIs create cost and availability risk",
    ]
    for i, t in enumerate(threats):
        y = 4.33 + i * 0.6
        rect(sl, 4.73, y, 5.0, 0.5, DARK2)
        rect(sl, 4.73, y, 0.04, 0.5, CORAL)
        txt(sl, f"⚠  {t}", 4.88, y+0.09, 4.75, 0.35, size=9.5, color=CORAL)

    footer_dark(sl)


# ─────────────────────────────────────────────────────────────────────────────
#  SLIDE 4 — STRATEGIC PROPOSALS  (light)
# ─────────────────────────────────────────────────────────────────────────────
def slide_strategy(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(sl, LIGHT)
    header_light(sl, "Research Report  ·  Section 4",
                  "Strategic Proposals for Cotiviti")

    proposals = [
        (EMERALD, "01", "Build a Policy Intelligence Layer",
         "Invest in a RAG-based internal platform that ingests all payer policy PDFs on publication "
         "and makes them queryable by analysts and adjudication systems in real time — eliminating "
         "manual review cycles and reducing prior-auth processing time from days to seconds.",
         "Impact: 60–80% reduction in analyst policy-review time per claim"),

        (AMBER, "02", "Automate Rule-to-Code Conversion",
         "Use LLM rule extraction to automatically convert written billing and coding policies into "
         "structured IF/THEN business rules that feed directly into claims adjudication engines — "
         "replacing manual rule coding and reducing update lag from weeks to hours.",
         "Impact: Faster policy-to-production cycles; fewer coding errors"),

        (CORAL, "03", "Deploy AI-Powered Audit Trail as a Product",
         "Instrument every AI coverage decision with a structured log capturing retrieved evidence, "
         "reasoning steps, and confidence scores. Position as a premium compliance product for "
         "health plan clients facing CMS audits and provider appeal volumes.",
         "Impact: Audit-ready documentation; reduced appeal liability"),
    ]

    for i, (accent, num, title, body_t, impact) in enumerate(proposals):
        y = 1.22 + i * 1.94
        rect(sl, 0.35, y, 9.3, 1.8, WHITE)
        rect(sl, 0.35, y, 9.3, 0.02, BORDER)
        rect(sl, 0.35, y+1.78, 9.3, 0.02, BORDER)
        # number badge
        rect(sl, 0.35, y, 0.75, 1.8, DARK)
        txt(sl, num, 0.35, y+0.65, 0.75, 0.52,
            size=18, bold=True, color=accent, align=PP_ALIGN.CENTER)
        # accent top line
        rect(sl, 1.1, y, 8.55, 0.04, accent)
        # content
        txt(sl, title,  1.22, y+0.1, 8.2, 0.36, size=13, bold=True, color=DARK)
        txt(sl, body_t, 1.22, y+0.5, 8.2, 0.9,  size=10, color=BODY)
        txt(sl, f"→  {impact}", 1.22, y+1.44, 8.2, 0.3,
            size=9.5, bold=True, color=accent, italic=True)

    footer_light(sl)


# ─────────────────────────────────────────────────────────────────────────────
#  SLIDE 5 — POC OVERVIEW  (dark)
# ─────────────────────────────────────────────────────────────────────────────
def slide_poc_overview(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(sl, DARK)
    header_dark(sl, "Proof of Concept", "IntelliPolicy AI — How It Works")

    # What it proves
    rect(sl, 0.35, 1.18, 9.3, 0.65, DARK2)
    rect(sl, 0.35, 1.18, 0.04, 0.65, EMERALD)
    txt(sl,
        "IntelliPolicy AI proves that written healthcare policy can be automatically ingested, "
        "queried in natural language, converted into structured business rules, and used to "
        "validate insurance claims — with a full audit trail on every decision.",
        0.5, 1.26, 9.0, 0.5, size=10.5, color=WHITE)

    # Pipeline diagram
    txt(sl, "5-STEP PROCESSING PIPELINE", 0.45, 1.99, 9, 0.26,
        size=8.5, bold=True, color=SLATE_D)

    # Same accent colours as the app (page.tsx step colours)
    steps = [
        (DARK,   F_UPLOAD,  "①\nUpload\nPDF",       "pdfplumber\nextracts text\nby page"),
        (DARK,   F_QA,      "②\nChunk &\nEmbed",    "512-token chunks\nBAA bge-small\n384-dim vectors"),
        (DARK,   F_COMPARE, "③\nHybrid\nSearch",    "70% semantic\n30% keyword\nfused ranking"),
        (DARK,   F_RULES,   "④\nLLM\nGenerate",     "Gemini / Claude\nstructured JSON\nwith citations"),
        (DARK,   F_CLAIMS,  "⑤\nAudit &\nValidate", "Rule extraction\nClaims check\nFull audit log"),
    ]
    for i, (bg, accent, title, body_t) in enumerate(steps):
        x = 0.35 + i * 1.88
        rect(sl, x, 2.32, 1.72, 2.5, DARK2)
        rect(sl, x, 2.32, 1.72, 0.04, accent)
        txt(sl, title, x+0.08, 2.38, 1.56, 0.65,
            size=9.5, bold=True, color=WHITE)
        txt(sl, body_t, x+0.08, 3.1, 1.56, 1.6, size=9.5, color=SLATE)
        if i < 4:
            txt(sl, "→", x+1.74, 3.35, 0.22, 0.38, size=13, bold=True, color=SLATE_D)

    # 6 features grid — using exact app accent colours
    txt(sl, "6 WORKING FEATURES", 0.45, 4.98, 9, 0.26, size=8.5, bold=True, color=SLATE_D)
    features = [
        (F_UPLOAD,  "📥 Upload Documents",  "Ingest any policy PDF"),
        (F_QA,      "🤖 AI Assistant",      "Natural language Q&A with citations"),
        (F_COMPARE, "⚖  Policy Compare",   "Version diff with risk scoring"),
        (F_RULES,   "📋 Rule Extraction",   "IF/THEN business rule parser"),
        (F_CLAIMS,  "🛡 Claims Validator",  "CPT + ICD-10 claim decision engine"),
        (F_AUDIT,   "🔎 Audit Trail",       "Full immutable decision log"),
    ]
    for i, (accent, name, desc) in enumerate(features):
        col = i % 3
        row = i // 3
        x = 0.35 + col * 3.12
        y = 5.33 + row * 0.72
        rect(sl, x, y, 2.95, 0.62, DARK2)
        rect(sl, x, y, 0.04, 0.62, accent)
        txt(sl, name, x+0.15, y+0.06, 2.7, 0.28, size=10, bold=True, color=WHITE)
        txt(sl, desc, x+0.15, y+0.35, 2.7, 0.24, size=9,  color=SLATE)

    footer_dark(sl)


# ─────────────────────────────────────────────────────────────────────────────
#  SLIDE 6 — DEMO WALKTHROUGH  (light)
# ─────────────────────────────────────────────────────────────────────────────
def slide_poc_demo(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(sl, LIGHT)
    header_light(sl, "Proof of Concept  ·  Live Demo", "Feature Walkthrough")

    demo_steps = [
        (F_UPLOAD,  "Step 1\nUpload",
         "Load Prior Auth Policy PDF → system chunks into 512-token segments,\nembeds with BAAI/bge-small-en-v1.5 → indexed in ~10 seconds."),
        (F_QA,      "Step 2\nAI Q&A",
         "Ask 'What requires prior authorization?' → RAG retrieves 5 chunks,\nfilters boilerplate → Gemini returns structured answer with page citations."),
        (F_COMPARE, "Step 3\nCompare",
         "Select two policy versions → AI surfaces every change: old value,\nnew value, risk level — in seconds instead of hours."),
        (F_RULES,   "Step 4\nRule Extraction",
         "Select document → Extract → LLM parses policy into IF/THEN business\nrules with CPT codes, plan types, and prior-auth flags. Export as JSON."),
        (F_CLAIMS,  "Step 5\nClaims Validator",
         "CPT code auto-travels from rules page → add diagnosis code → Validate.\nReturns: Approved / Denied / Needs Review + policy source + confidence."),
        (F_AUDIT,   "Step 6\nAudit Trail",
         "Every AI decision logged with: retrieved pages, reasoning steps,\nevidence quotes, confidence score — exportable compliance record."),
    ]

    for i, (accent, label, body_t) in enumerate(demo_steps):
        col = i % 2
        row = i // 2
        x = 0.35 + col * 4.85
        y = 1.22 + row * 1.98
        # card
        rect(sl, x, y, 4.65, 1.82, WHITE)
        rect(sl, x, y, 4.65, 0.02, BORDER)
        rect(sl, x, y+1.8, 4.65, 0.02, BORDER)
        rect(sl, x, y, 4.65, 0.04, accent)   # accent top strip
        # left label
        rect(sl, x, y, 0.85, 1.82, DARK)
        txt(sl, label, x+0.06, y+0.55, 0.73, 0.75,
            size=9, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        # body
        txt(sl, body_t, x+0.98, y+0.15, 3.52, 1.55, size=10, color=BODY)

    footer_light(sl)


# ─────────────────────────────────────────────────────────────────────────────
#  SLIDE 7 — CLOSING  (dark)
# ─────────────────────────────────────────────────────────────────────────────
def slide_close(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(sl, DARK)
    rect(sl, 0, 0, 0.12, 7.5, EMERALD)

    txt(sl, "C O T I V I T I  ·  I N T E R N  A S S E S S M E N T",
        0.32, 0.2, 9.5, 0.36, size=9, bold=True, color=SLATE_D)
    rect(sl, 0.32, 0.72, 9.2, 0.02, DARK3)

    txt(sl, "Thank You", 0.32, 0.9, 9, 0.85, size=50, bold=True, color=WHITE)
    txt(sl, "Questions & Discussion", 0.32, 1.85, 9, 0.46, size=18, color=SLATE)
    rect(sl, 0.32, 2.46, 9.2, 0.02, DARK3)

    summary = [
        (EMERALD, "✓", "Topic 3 — Content Management in Healthcare: policies, summarization, rule conversion"),
        (EMERALD, "✓", "POC proves: PDF → RAG → structured rules → claims validation → audit trail"),
        (EMERALD, "✓", "3 strategic proposals: Policy Intelligence Layer · Rule Automation · AI Audit Trail"),
        (EMERALD, "✓", "Directly relevant to Cotiviti's payment accuracy and clinical intelligence products"),
    ]
    for i, (c, mark, text) in enumerate(summary):
        y = 2.65 + i * 0.56
        txt(sl, mark, 0.38, y, 0.4, 0.46, size=13, bold=True, color=c)
        txt(sl, text, 0.78, y, 8.7, 0.46, size=11, color=WHITE)

    rect(sl, 0.32, 4.92, 9.2, 0.02, DARK3)

    contact = [
        ("Developer",    "Sohith Kampalli  ·  sohithkampalli@gmail.com"),
        ("GitHub",       "github.com/sohithk2002/intellipolicy-ai"),
        ("Submitted to", "jesus.hurtado@cotiviti.com"),
        ("Institution",  "University of North Texas"),
    ]
    for i, (k, v) in enumerate(contact):
        y = 5.1 + i * 0.42
        txt(sl, k + ":", 0.35, y, 2.0, 0.36, size=10, bold=True, color=SLATE_D)
        txt(sl, v,       2.42, y, 7.3, 0.36, size=10, color=WHITE)

    rect(sl, 0.32, 6.88, 9.2, 0.02, DARK3)
    txt(sl, '"Turning written policy into intelligent, auditable decisions."',
        0.32, 6.58, 9.4, 0.38, size=10.5, italic=True,
        color=SLATE, align=PP_ALIGN.CENTER)

    footer_dark(sl)


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
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
    print(f"✓  PPT saved → {path}")
