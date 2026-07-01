"""
CEO-style deck — all slides light/white, dark text, professional.
Palette: white bg, #111827 headings, #374151 body, thin emerald/amber accents.
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import datetime, pathlib

OUT = pathlib.Path("/Users/sohithkampalli/cotivity/intellipolicy-ai")

# ── palette ───────────────────────────────────────────────────────────────────
WHITE    = RGBColor(0xFF, 0xFF, 0xFF)
BG       = RGBColor(0xFA, 0xFA, 0xFB)   # near-white slide bg
CARD     = RGBColor(0xF3, 0xF4, 0xF6)   # light card fill
BORDER   = RGBColor(0xE5, 0xE7, 0xEB)   # card border
HEAD     = RGBColor(0x11, 0x18, 0x27)   # #111827 heading
BODY     = RGBColor(0x37, 0x41, 0x51)   # #374151 body
MUTED    = RGBColor(0x6B, 0x72, 0x80)   # #6B7280 labels / captions
EM       = RGBColor(0x05, 0x96, 0x69)   # #059669 emerald (darker, more pro)
EM_LIGHT = RGBColor(0xD1, 0xFA, 0xE5)   # emerald tint bg
AM       = RGBColor(0xD9, 0x77, 0x06)   # #D97706 amber
AM_LIGHT = RGBColor(0xFE, 0xF3, 0xC7)   # amber tint bg
RD       = RGBColor(0xDC, 0x26, 0x26)   # #DC2626 red
RD_LIGHT = RGBColor(0xFE, 0xE2, 0xE2)   # red tint bg
SL       = RGBColor(0x64, 0x74, 0x8B)   # slate
DARK2    = RGBColor(0x1F, 0x29, 0x37)   # cover bg

# ── helpers ───────────────────────────────────────────────────────────────────
def set_bg(slide, c: RGBColor):
    f = slide.background.fill; f.solid(); f.fore_color.rgb = c

def box(slide, l, t, w, h, fill: RGBColor):
    s = slide.shapes.add_shape(1, Inches(l), Inches(t), Inches(w), Inches(h))
    s.line.fill.background(); s.fill.solid(); s.fill.fore_color.rgb = fill
    return s

def lined_box(slide, l, t, w, h, fill: RGBColor, border: RGBColor):
    """Card with visible border."""
    s = slide.shapes.add_shape(1, Inches(l), Inches(t), Inches(w), Inches(h))
    s.fill.solid(); s.fill.fore_color.rgb = fill
    s.line.color.rgb = border; s.line.width = Pt(0.75)
    return s

def t(slide, text, l, top, w, h, size=11, bold=False, color=BODY,
      align=PP_ALIGN.LEFT, italic=False):
    tb = slide.shapes.add_textbox(Inches(l), Inches(top), Inches(w), Inches(h))
    tb.word_wrap = True
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size); r.font.bold = bold; r.font.italic = italic
    r.font.color.rgb = color; r.font.name = "Calibri"
    return tb

def lines(slide, items, l, top, w, h, size=10.5, color=BODY, gap=4):
    tb = slide.shapes.add_textbox(Inches(l), Inches(top), Inches(w), Inches(h))
    tb.word_wrap = True; tf = tb.text_frame; tf.word_wrap = True
    for i, line in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap)
        r = p.add_run(); r.text = line
        r.font.size = Pt(size); r.font.color.rgb = color; r.font.name = "Calibri"
    return tb

def slide_header(slide, label, title):
    """Standard light header used on every slide."""
    # thin top colour strip
    box(slide, 0, 0, 10, 0.06, EM)
    # label
    t(slide, label.upper(), 0.45, 0.14, 9.1, 0.28,
      size=8.5, bold=True, color=MUTED)
    # title
    t(slide, title, 0.45, 0.42, 9.1, 0.62,
      size=26, bold=True, color=HEAD)
    # divider
    box(slide, 0.45, 1.04, 9.1, 0.015, BORDER)

def footer(slide):
    box(slide, 0, 7.22, 10, 0.28, WHITE)
    box(slide, 0, 7.22, 10, 0.015, BORDER)
    t(slide, "IntelliPolicy AI  ·  Cotiviti Intern Assessment  ·  Sohith Kampalli",
      0.45, 7.25, 9.1, 0.22, size=8.5, color=MUTED, align=PP_ALIGN.CENTER)

def accent_card(slide, l, top, w, h, accent: RGBColor, title, body_text,
                title_size=11, body_size=10):
    """White card with thin left accent bar."""
    lined_box(slide, l, top, w, h, WHITE, BORDER)
    box(slide, l, top, 0.04, h, accent)
    t(slide, title,     l+0.14, top+0.1,  w-0.2, 0.3,
      size=title_size, bold=True, color=HEAD)
    t(slide, body_text, l+0.14, top+0.44, w-0.2, h-0.55,
      size=body_size, color=BODY)

def num_card(slide, l, top, w, h, num, accent, title, body_text, impact):
    """Numbered proposal card."""
    lined_box(slide, l, top, w, h, WHITE, BORDER)
    box(slide, l, top, w, 0.04, accent)          # top accent strip
    # number circle bg
    box(slide, l+0.12, top+0.12, 0.44, 0.44, CARD)
    t(slide, num, l+0.12, top+0.12, 0.44, 0.44,
      size=13, bold=True, color=accent, align=PP_ALIGN.CENTER)
    t(slide, title,     l+0.68, top+0.1,  w-0.82, 0.34,
      size=12, bold=True, color=HEAD)
    t(slide, body_text, l+0.68, top+0.48, w-0.82, h-0.75,
      size=10, color=BODY)
    t(slide, f"→  {impact}", l+0.68, top+h-0.3, w-0.82, 0.27,
      size=9.5, bold=True, color=accent, italic=True)


# ─────────────────────────────────────────────────────────────────────────────
#  SLIDE 1 — COVER
# ─────────────────────────────────────────────────────────────────────────────
def slide_cover(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(sl, WHITE)

    # top accent bar
    box(sl, 0, 0, 10, 0.06, EM)
    box(sl, 0, 0.06, 10, 0.01, BORDER)

    # company label
    t(sl, "COTIVITI  ·  INTERN ASSESSMENT  ·  TOPIC 3",
      0.55, 0.25, 9, 0.3, size=9, bold=True, color=MUTED)

    # main title
    t(sl, "IntelliPolicy AI", 0.55, 0.72, 9, 1.1,
      size=56, bold=True, color=HEAD)

    # sub
    t(sl, "Intelligent Policy Content Management for Healthcare",
      0.55, 1.9, 9, 0.48, size=17, color=BODY)

    # divider
    box(sl, 0.55, 2.55, 8.9, 0.015, BORDER)

    # meta rows
    meta = [
        ("Submitted by",  "Sohith Kampalli"),
        ("Assessment",    "Software Engineer Intern  ·  University of North Texas"),
        ("Topic",         "Billing & Coding Policies  ·  Summarization  ·  Rule Conversion"),
        ("POC Stack",     "Next.js 14  ·  FastAPI  ·  BAAI/bge-small  ·  RAG Pipeline"),
        ("Date",          datetime.date.today().strftime("%B %d, %Y")),
    ]
    for i, (k, v) in enumerate(meta):
        y = 2.73 + i * 0.52
        t(sl, k,  0.55, y, 1.9,  0.42, size=10, bold=True,  color=MUTED)
        t(sl, v,  2.55, y, 7.0,  0.42, size=10,              color=BODY)

    # bottom github tag
    box(sl, 0.55, 6.55, 4.4, 0.34, EM_LIGHT)
    box(sl, 0.55, 6.55, 0.04, 0.34, EM)
    t(sl, "github.com/sohithk2002/intellipolicy-ai",
      0.7, 6.60, 4.1, 0.24, size=9, bold=True, color=EM)

    footer(sl)


# ─────────────────────────────────────────────────────────────────────────────
#  SLIDE 2 — TOPIC DEFINITION
# ─────────────────────────────────────────────────────────────────────────────
def slide_topic(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(sl, WHITE)
    slide_header(sl, "Research Report  ·  Section 1",
                 "What Is Content Management in Health Care?")

    # definition block
    lined_box(sl, 0.45, 1.2, 9.1, 1.12, EM_LIGHT, BORDER)
    box(sl, 0.45, 1.2, 0.04, 1.12, EM)
    t(sl, "Definition", 0.62, 1.26, 2, 0.26, size=8.5, bold=True, color=EM)
    t(sl,
      "The systematic ingestion, organisation, and transformation of clinical and administrative "
      "documents — billing and coding policies, clinical practice guidelines, and payer-provider "
      "contracts — into structured, machine-readable formats enabling automated decision-making, "
      "audit, and compliance.",
      0.62, 1.52, 8.75, 0.72, size=11, color=BODY)

    # three pillars
    pillars = [
        (EM, "Billing & Coding Policies",
         "CMS manuals · CPT/ICD-10 crosswalks\nPrior-auth rules · Frequency limits\nUpdated quarterly across 50+ payers"),
        (AM, "Clinical Practice Guidelines",
         "Evidence-based care pathways\nMedical necessity criteria\nVary by plan type and state"),
        (SL, "Payer-Provider Contracts",
         "Fee schedules · Bundled payments\nCarve-outs · Network terms\nRenegotiated annually"),
    ]
    for i, (accent, title, body_txt) in enumerate(pillars):
        x = 0.45 + i * 3.07
        lined_box(sl, x, 2.46, 2.92, 3.32, WHITE, BORDER)
        box(sl, x, 2.46, 2.92, 0.04, accent)
        t(sl, title,    x+0.18, 2.6,  2.6, 0.38, size=11, bold=True, color=HEAD)
        t(sl, body_txt, x+0.18, 3.05, 2.6, 1.6,  size=10.5, color=BODY)
        # small pill label
        box(sl, x+0.18, 5.5, 1.1, 0.24, CARD)
        t(sl, f"0{i+1}", x+0.18, 5.5, 1.1, 0.24,
          size=9, bold=True, color=accent, align=PP_ALIGN.CENTER)

    # arrows
    for xi in [3.4, 6.5]:
        t(sl, "→", xi, 3.95, 0.3, 0.35, size=14, bold=True, color=MUTED)

    footer(sl)


# ─────────────────────────────────────────────────────────────────────────────
#  SLIDE 3 — TRENDS + OPP + THREATS
# ─────────────────────────────────────────────────────────────────────────────
def slide_trends(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(sl, WHITE)
    slide_header(sl, "Research Report  ·  Sections 2 & 3",
                 "Trends  ·  Opportunities  ·  Threats")

    # ── Trends (left column) ──────────────────────────────────────────────
    t(sl, "KEY TRENDS", 0.45, 1.18, 3.8, 0.26,
      size=8.5, bold=True, color=MUTED)
    trends = [
        ("LLMs for Policy",
         "GPT-4, Gemini, Claude read 200-page\nPDFs and answer coverage questions\nwith page-level citations."),
        ("RAG Pipelines",
         "Retrieval-Augmented Generation grounds\nAI answers in specific document evidence —\ncritical for regulatory accuracy."),
        ("Rule Extraction",
         "NLP converts written policy into machine-\nreadable IF/THEN logic for automated\nclaims adjudication."),
        ("Automated Diff",
         "AI detects changes between policy versions\ninstantly — replacing manual review\ncycles that take weeks."),
    ]
    for i, (title, body_txt) in enumerate(trends):
        y = 1.5 + i * 1.3
        lined_box(sl, 0.45, y, 3.85, 1.18, WHITE, BORDER)
        box(sl, 0.45, y, 0.04, 1.18, SL)
        t(sl, title,    0.62, y+0.1,  3.55, 0.3, size=10, bold=True, color=HEAD)
        t(sl, body_txt, 0.62, y+0.44, 3.55, 0.68, size=9.5, color=BODY)

    # ── Opportunities ─────────────────────────────────────────────────────
    t(sl, "OPPORTUNITIES FOR COTIVITI", 4.5, 1.18, 5.1, 0.26,
      size=8.5, bold=True, color=EM)
    opps = [
        "Automate prior-auth review — 60–80% less analyst handle time per claim",
        "Real-time CPT/ICD-10 adjudication against extracted policy rules",
        "Instant policy version diff — surface coverage changes on publication day",
        "Full audit trail per AI decision — defensible compliance documentation",
    ]
    for i, o in enumerate(opps):
        y = 1.5 + i * 0.64
        lined_box(sl, 4.5, y, 5.1, 0.55, EM_LIGHT, BORDER)
        box(sl, 4.5, y, 0.04, 0.55, EM)
        t(sl, f"✓  {o}", 4.67, y+0.1, 4.8, 0.36, size=9.5, color=EM)

    # ── Threats ────────────────────────────────────────────────────────────
    t(sl, "THREATS & CHALLENGES", 4.5, 4.15, 5.1, 0.26,
      size=8.5, bold=True, color=RD)
    threats = [
        "LLM hallucination in clinical context — wrong decisions risk patient harm",
        "HIPAA compliance — AI near PHI must meet security rule requirements",
        "Model drift — policies update quarterly; embeddings must stay current",
        "Vendor dependency — third-party LLM APIs create cost and availability risk",
    ]
    for i, thr in enumerate(threats):
        y = 4.46 + i * 0.64
        lined_box(sl, 4.5, y, 5.1, 0.55, RD_LIGHT, BORDER)
        box(sl, 4.5, y, 0.04, 0.55, RD)
        t(sl, f"⚠  {thr}", 4.67, y+0.1, 4.8, 0.36, size=9.5, color=RD)

    footer(sl)


# ─────────────────────────────────────────────────────────────────────────────
#  SLIDE 4 — STRATEGIC PROPOSALS
# ─────────────────────────────────────────────────────────────────────────────
def slide_strategy(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(sl, WHITE)
    slide_header(sl, "Research Report  ·  Section 4",
                 "Strategic Proposals for Cotiviti")

    proposals = [
        (EM, "01", "Build a Policy Intelligence Layer",
         "A RAG-based internal platform that ingests all payer policy PDFs on publication and "
         "makes them instantly queryable by analysts and adjudication systems — eliminating manual "
         "review cycles and reducing prior-auth processing from days to seconds.",
         "60–80% reduction in analyst policy-review time per claim"),

        (AM, "02", "Automate Rule-to-Code Conversion",
         "LLM rule extraction automatically converts written billing and coding policies into "
         "structured IF/THEN business rules that feed directly into claims adjudication engines — "
         "replacing manual rule coding and reducing update lag from weeks to hours.",
         "Faster policy-to-production cycles with fewer coding errors"),

        (RD, "03", "Deploy AI-Powered Audit Trail as a Product",
         "Every AI coverage decision logged with retrieved evidence, reasoning steps, and confidence "
         "scores. Position as a premium compliance product for health plan clients facing CMS audits "
         "and provider appeal volumes — a defensible, scalable documentation solution.",
         "Audit-ready documentation and reduced appeal liability"),
    ]

    for i, (accent, num, title, body_txt, impact) in enumerate(proposals):
        y = 1.22 + i * 1.94
        num_card(sl, 0.45, y, 9.1, 1.8, num, accent, title, body_txt, impact)

    footer(sl)


# ─────────────────────────────────────────────────────────────────────────────
#  SLIDE 5 — POC OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
def slide_poc(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(sl, WHITE)
    slide_header(sl, "Proof of Concept",
                 "IntelliPolicy AI — How It Works")

    # What it proves
    lined_box(sl, 0.45, 1.2, 9.1, 0.72, EM_LIGHT, BORDER)
    box(sl, 0.45, 1.2, 0.04, 0.72, EM)
    t(sl, "What it proves", 0.62, 1.26, 3, 0.24, size=8.5, bold=True, color=EM)
    t(sl,
      "Written healthcare policy can be automatically ingested, queried in natural language, "
      "converted into structured business rules, and used to validate insurance claims — "
      "with a full audit trail on every single decision.",
      0.62, 1.5, 8.75, 0.36, size=11, color=BODY)

    # Pipeline steps
    t(sl, "5-STEP PROCESSING PIPELINE", 0.45, 2.07, 9, 0.26,
      size=8.5, bold=True, color=MUTED)

    step_accents = [HEAD, SL, SL, EM, AM]
    step_titles  = ["① Upload PDF", "② Chunk & Embed", "③ Hybrid Search",
                    "④ LLM Generate", "⑤ Audit & Validate"]
    step_bodies  = [
        "pdfplumber\nextracts text\nby page",
        "512-token chunks\nBAA bge-small\n384-dim vectors",
        "70% semantic\n30% keyword\nfused ranking",
        "Gemini / Claude\nstructured JSON\nwith citations",
        "Rule extraction\nClaims check\nAudit log",
    ]
    for i in range(5):
        x = 0.45 + i * 1.84
        lined_box(sl, x, 2.38, 1.72, 2.45, WHITE, BORDER)
        box(sl, x, 2.38, 1.72, 0.04, step_accents[i])
        t(sl, step_titles[i], x+0.1, 2.48, 1.52, 0.45,
          size=9.5, bold=True, color=HEAD)
        t(sl, step_bodies[i], x+0.1, 2.98, 1.52, 1.7,
          size=9.5, color=BODY)
        if i < 4:
            t(sl, "→", x+1.74, 3.4, 0.18, 0.3, size=11, color=MUTED)

    # 6 features
    t(sl, "6 WORKING FEATURES", 0.45, 4.98, 9, 0.26, size=8.5, bold=True, color=MUTED)
    feats = [
        (HEAD, "📥 Upload Documents",  "Ingest any policy PDF"),
        (SL,   "🤖 AI Assistant",      "Natural language Q&A with citations"),
        (SL,   "⚖  Policy Compare",   "Version diff with risk scoring"),
        (EM,   "📋 Rule Extraction",   "IF/THEN business rule parser"),
        (AM,   "🛡 Claims Validator",  "CPT + ICD-10 claim decision engine"),
        (RD,   "🔎 Audit Trail",       "Full immutable decision log"),
    ]
    for i, (accent, name, desc) in enumerate(feats):
        col = i % 3; row = i // 3
        x = 0.45 + col * 3.07
        y = 5.3  + row * 0.72
        lined_box(sl, x, y, 2.92, 0.62, WHITE, BORDER)
        box(sl, x, y, 0.04, 0.62, accent)
        t(sl, name, x+0.14, y+0.07, 2.65, 0.26, size=10,  bold=True, color=HEAD)
        t(sl, desc, x+0.14, y+0.35, 2.65, 0.22, size=9.5, color=MUTED)

    footer(sl)


# ─────────────────────────────────────────────────────────────────────────────
#  SLIDE 6 — DEMO WALKTHROUGH
# ─────────────────────────────────────────────────────────────────────────────
def slide_demo(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(sl, WHITE)
    slide_header(sl, "Proof of Concept  ·  Live Demo", "Feature Walkthrough")

    accents = [HEAD, SL, SL, EM, AM, RD]
    steps = [
        ("Step 1  Upload",
         "Load Prior Auth Policy PDF → system chunks into 512-token segments, embeds with "
         "BAAI/bge-small-en-v1.5 → fully indexed in under 10 seconds."),
        ("Step 2  AI Q&A",
         "Ask a natural language question → RAG retrieves 5 chunks, filters boilerplate → "
         "Gemini returns structured answer with page citations and confidence score."),
        ("Step 3  Compare",
         "Select two policy versions → AI surfaces every change: old value, new value, "
         "risk level — in seconds instead of reading both documents manually."),
        ("Step 4  Rule Extraction",
         "Extract → LLM parses policy into IF/THEN business rules with CPT codes, plan "
         "types, prior-auth flags. Export as JSON to feed downstream claims engines."),
        ("Step 5  Claims Validator",
         "CPT code auto-travels from rules page → add diagnosis code → Validate. Returns "
         "Approved / Denied / Needs Review with policy source and confidence score."),
        ("Step 6  Audit Trail",
         "Every AI decision logged with retrieved pages, reasoning steps, evidence quotes, "
         "and confidence score — exportable compliance record for CMS audits."),
    ]

    for i, (label, body_txt) in enumerate(steps):
        col = i % 2; row = i // 2
        x = 0.45 + col * 4.82
        y = 1.2  + row * 1.98
        lined_box(sl, x, y, 4.65, 1.82, WHITE, BORDER)
        box(sl, x, y, 4.65, 0.04, accents[i])
        # step number
        box(sl, x+0.12, y+0.14, 0.38, 0.38, CARD)
        t(sl, str(i+1), x+0.12, y+0.14, 0.38, 0.38,
          size=11, bold=True, color=accents[i], align=PP_ALIGN.CENTER)
        t(sl, label,    x+0.62, y+0.12, 3.9, 0.32, size=11, bold=True, color=HEAD)
        t(sl, body_txt, x+0.62, y+0.48, 3.9, 1.25, size=10, color=BODY)

    footer(sl)


# ─────────────────────────────────────────────────────────────────────────────
#  SLIDE 7 — CLOSING
# ─────────────────────────────────────────────────────────────────────────────
def slide_close(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(sl, WHITE)

    box(sl, 0, 0, 10, 0.06, EM)
    box(sl, 0, 0.06, 10, 0.01, BORDER)

    t(sl, "COTIVITI  ·  INTERN ASSESSMENT",
      0.55, 0.2, 9, 0.28, size=9, bold=True, color=MUTED)

    t(sl, "Thank You", 0.55, 0.6, 9, 1.0,
      size=52, bold=True, color=HEAD)
    t(sl, "Questions & Discussion",
      0.55, 1.7, 9, 0.44, size=17, color=BODY)

    box(sl, 0.55, 2.3, 8.9, 0.015, BORDER)

    bullets = [
        (EM, "Topic 3 — Content Management in Healthcare: policies, summarization, rule conversion"),
        (EM, "POC proves: PDF → RAG → structured rules → claims validation → audit trail"),
        (EM, "3 proposals: Policy Intelligence Layer  ·  Rule Automation  ·  AI Audit Trail"),
        (EM, "Directly relevant to Cotiviti's payment accuracy and clinical intelligence products"),
    ]
    for i, (c, txt_) in enumerate(bullets):
        y = 2.48 + i * 0.58
        box(sl, 0.55, y+0.12, 0.22, 0.22, EM_LIGHT)
        t(sl, "✓", 0.55, y+0.12, 0.22, 0.22,
          size=9, bold=True, color=EM, align=PP_ALIGN.CENTER)
        t(sl, txt_, 0.88, y+0.08, 8.7, 0.42, size=11, color=BODY)

    box(sl, 0.55, 4.85, 8.9, 0.015, BORDER)

    contact = [
        ("Developer",    "Sohith Kampalli  ·  sohithkampalli@gmail.com"),
        ("GitHub",       "github.com/sohithk2002/intellipolicy-ai"),
        ("Submitted to", "jesus.hurtado@cotiviti.com"),
        ("Institution",  "University of North Texas"),
    ]
    for i, (k, v) in enumerate(contact):
        y = 5.05 + i * 0.44
        t(sl, k, 0.55, y, 1.9, 0.38, size=10, bold=True, color=MUTED)
        t(sl, v, 2.55, y, 7.2, 0.38, size=10, color=BODY)

    box(sl, 0.55, 6.82, 8.9, 0.015, BORDER)
    t(sl, '"Turning written policy into intelligent, auditable decisions."',
      0.55, 6.88, 9.1, 0.32, size=10, italic=True, color=MUTED,
      align=PP_ALIGN.CENTER)

    footer(sl)


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    prs = Presentation()
    prs.slide_width  = Inches(10)
    prs.slide_height = Inches(7.5)

    slide_cover(prs)
    slide_topic(prs)
    slide_trends(prs)
    slide_strategy(prs)
    slide_poc(prs)
    slide_demo(prs)
    slide_close(prs)

    path = OUT / "IntelliPolicy_AI_Presentation.pptx"
    prs.save(str(path))
    print(f"✓  PPT saved → {path}")
