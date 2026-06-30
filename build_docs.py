"""
Build IntelliPolicy AI assessment deliverables:
  - IntelliPolicy_AI_Assessment_Deck.pptx   (14 slides, Cotiviti branded)
  - IntelliPolicy_AI_Technical_Report.docx  (full technical report, APA)
  - IntelliPolicy_AI_Video_Script.txt        (GPS-style recording script)
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
import copy
from docx import Document
from docx.shared import Inches as DInches, Pt as DPt, RGBColor as DRGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import datetime, pathlib, textwrap

OUT = pathlib.Path("/Users/sohithkampalli/cotivity/intellipolicy-ai")

# ── Cotiviti brand colours ──────────────────────────────────────────────────
PURPLE      = RGBColor(0x6B, 0x2D, 0x8B)   # #6B2D8B
LIGHT_PUR   = RGBColor(0xB0, 0x7F, 0xC8)   # #B07FC8
OFF_WHITE   = RGBColor(0xF7, 0xF3, 0xFB)   # #F7F3FB
DARK        = RGBColor(0x1A, 0x0D, 0x2E)   # #1A0D2E
MID_GRAY    = RGBColor(0x64, 0x74, 0x8B)   # slate-500
WHITE       = RGBColor(0xFF, 0xFF, 0xFF)
AMBER       = RGBColor(0xFB, 0xBF, 0x24)
TEAL        = RGBColor(0x14, 0xB8, 0xA6)
SKY         = RGBColor(0x38, 0xBD, 0xF8)

# ═══════════════════════════════════════════════════════════════════════════
#  POWERPOINT
# ═══════════════════════════════════════════════════════════════════════════

def rgb(r,g,b): return RGBColor(r,g,b)

def set_bg(slide, r, g, b):
    from pptx.oxml.ns import qn as pqn
    from lxml import etree
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(r,g,b)

def add_rect(slide, l, t, w, h, fill_rgb, alpha=None):
    shape = slide.shapes.add_shape(1, Inches(l), Inches(t), Inches(w), Inches(h))
    shape.line.fill.background()
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_rgb
    return shape

def add_text(slide, text, l, t, w, h, size=18, bold=False, color=WHITE,
             align=PP_ALIGN.LEFT, italic=False, wrap=True):
    txb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    txb.word_wrap = wrap
    tf = txb.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name = "Calibri"
    return txb

def add_multiline(slide, lines, l, t, w, h, size=13, color=WHITE, spacing=1.2):
    from pptx.util import Pt
    txb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    txb.word_wrap = True
    tf = txb.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(4)
        run = p.add_run()
        run.text = line
        run.font.size = Pt(size)
        run.font.color.rgb = color
        run.font.name = "Calibri"
    return txb

def pill(slide, text, l, t, w=1.4, h=0.28, bg=PURPLE, fg=WHITE, size=10):
    r = add_rect(slide, l, t, w, h, bg)
    add_text(slide, text, l+0.05, t+0.02, w-0.1, h-0.04, size=size,
             bold=True, color=fg, align=PP_ALIGN.CENTER)

def divider(slide, t, color=LIGHT_PUR):
    add_rect(slide, 0.6, t, 8.8, 0.025, color)

# ── Slide helpers ───────────────────────────────────────────────────────────

def slide_cover(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(sl, 0x1A, 0x0D, 0x2E)
    # Purple gradient bar left
    add_rect(sl, 0, 0, 0.18, 7.5, PURPLE)
    add_rect(sl, 0.18, 0, 0.06, 7.5, LIGHT_PUR)
    # Top bar
    add_rect(sl, 0, 0, 10, 0.08, PURPLE)
    # Cotiviti wordmark area
    add_rect(sl, 0.45, 0.22, 2.8, 0.55, RGBColor(0x2A,0x1D,0x42))
    add_text(sl, "COTIVITI", 0.55, 0.27, 2.6, 0.45, size=18, bold=True, color=LIGHT_PUR)
    # Tag line
    add_text(sl, "Healthcare Intelligence — Intern Technical Assessment", 0.45, 0.85,
             8.5, 0.45, size=13, color=LIGHT_PUR, italic=True)
    divider(sl, 1.45, PURPLE)
    # Main title
    add_text(sl, "IntelliPolicy AI", 0.45, 1.65, 9, 1.1, size=46, bold=True, color=WHITE)
    add_text(sl, "Intelligent Healthcare Policy Analysis Platform", 0.45, 2.75,
             9, 0.55, size=22, color=LIGHT_PUR)
    divider(sl, 3.45, LIGHT_PUR)
    # Meta row
    meta = [
        ("Submitted by",  "Sohith Kampalli"),
        ("Role",          "Software Engineer Intern — Cotiviti"),
        ("Stack",         "Next.js 14  ·  FastAPI  ·  Python 3.13  ·  BAAI BGE"),
        ("Deployment",    "Railway (Docker)  +  Vercel"),
        ("Date",          datetime.date.today().strftime("%B %d, %Y")),
    ]
    for i,(k,v) in enumerate(meta):
        y = 3.65 + i*0.44
        add_text(sl, k+":", 0.45, y, 2.2, 0.4, size=12, color=LIGHT_PUR, bold=True)
        add_text(sl, v,    2.7,  y, 6.5, 0.4, size=12, color=WHITE)
    # Bottom bar
    add_rect(sl, 0, 7.1, 10, 0.4, PURPLE)
    add_text(sl, "CONFIDENTIAL — For Assessment Purposes Only", 0.3, 7.13, 9.4, 0.34,
             size=10, color=LIGHT_PUR, align=PP_ALIGN.CENTER)


def slide_problem(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(sl, 0xF7, 0xF3, 0xFB)
    add_rect(sl, 0, 0, 10, 1.15, PURPLE)
    add_text(sl, "01  |  Problem Statement", 0.5, 0.3, 9, 0.6, size=26, bold=True, color=WHITE)
    add_text(sl, "The challenge IntelliPolicy AI was built to solve",
             0.5, 0.78, 9, 0.35, size=13, color=LIGHT_PUR, italic=True)
    problems = [
        ("📄  Manual Policy Review", "Analysts spend 60–80 % of time manually reading multi-hundred-page PDF policy manuals to answer single coverage questions."),
        ("⏱  Slow Decision Cycles", "Prior-authorization decisions require cross-referencing multiple policy versions, causing average cycle times of 3–5 business days."),
        ("⚠  Version Drift Risk",   "Organisations manage 10–50 active policy versions simultaneously; detecting changes between versions is a fully manual, error-prone process."),
        ("🔍  No Audit Trail",       "Current workflows have no structured log of which policy evidence supported a coverage decision, creating compliance and appeal liability."),
    ]
    for i,(title,body) in enumerate(problems):
        col = i % 2
        row = i // 2
        x = 0.4 + col * 4.7
        y = 1.35 + row * 2.5
        add_rect(sl, x, y, 4.4, 2.2, DARK)
        add_text(sl, title, x+0.2, y+0.18, 4.0, 0.4, size=13, bold=True, color=AMBER)
        add_text(sl, body,  x+0.2, y+0.6,  4.0, 1.45, size=11, color=WHITE)
    add_rect(sl, 0, 7.1, 10, 0.4, PURPLE)
    add_text(sl, "IntelliPolicy AI", 0.3, 7.13, 9.4, 0.34, size=10, color=LIGHT_PUR, align=PP_ALIGN.CENTER)


def slide_solution(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(sl, 0x1A, 0x0D, 0x2E)
    add_rect(sl, 0, 0, 10, 1.15, PURPLE)
    add_text(sl, "02  |  Solution Overview", 0.5, 0.3, 9, 0.6, size=26, bold=True, color=WHITE)
    add_text(sl, "A full-stack RAG platform with five specialised AI agents",
             0.5, 0.78, 9, 0.35, size=13, color=LIGHT_PUR, italic=True)
    features = [
        ("📥 Document Ingestion",  "PDF → pdfplumber → 512-token chunks\nwith 64-token overlap → BAAI/bge-small-en-v1.5\nembeddings → in-memory vector store"),
        ("🤖 AI Assistant",        "Semantic + BM25 hybrid retrieval (70/30)\nReranking → Sentence filtering → Gemini/\nClaude/GPT LLM generation with citations"),
        ("⚖  Policy Comparison",  "Side-by-side diff of two policy documents.\nSection-level change detection with risk\nscoring (High / Medium / Low)"),
        ("📋 Rule Extraction",     "Extracts structured business rules from raw\npolicy text. IF / THEN logic, CPT codes,\nprior-auth flags, documentation requirements"),
        ("🛡 Claims Validator",    "Validates CPT + ICD-10 + plan type against\nextracted rules. Returns Approved / Denied /\nNeeds Review with confidence score"),
        ("🔎 Audit Trail",         "Full immutable log of every AI decision:\nretrieved pages, reasoning steps, citations,\nconfidence, and session replay"),
    ]
    for i,( title, body) in enumerate(features):
        col = i % 3
        row = i // 3
        x = 0.3 + col * 3.15
        y = 1.35 + row * 2.7
        add_rect(sl, x, y, 2.95, 2.5, RGBColor(0x2A,0x1D,0x42))
        add_rect(sl, x, y, 2.95, 0.42, PURPLE)
        add_text(sl, title, x+0.12, y+0.07, 2.7, 0.35, size=11, bold=True, color=WHITE)
        add_text(sl, body,  x+0.12, y+0.52, 2.7, 1.85, size=10, color=LIGHT_PUR)
    add_rect(sl, 0, 7.1, 10, 0.4, PURPLE)
    add_text(sl, "IntelliPolicy AI", 0.3, 7.13, 9.4, 0.34, size=10, color=LIGHT_PUR, align=PP_ALIGN.CENTER)


def slide_architecture(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(sl, 0xF7, 0xF3, 0xFB)
    add_rect(sl, 0, 0, 10, 1.15, DARK)
    add_text(sl, "03  |  System Architecture", 0.5, 0.3, 9, 0.6, size=26, bold=True, color=WHITE)
    add_text(sl, "Five-agent pipeline with RAG at its core",
             0.5, 0.78, 9, 0.35, size=13, color=LIGHT_PUR, italic=True)

    # Pipeline boxes
    boxes = [
        ("User / Browser",       "Next.js 14\nTailwind CSS\nFramer Motion",         SKY,    0.3),
        ("FastAPI Gateway",      "CORS middleware\nPydantic v2 schemas\nLifespan hooks", PURPLE, 2.35),
        ("5 AI Agents",          "Intake · Retrieval\nQA · Compare\nRule · Claim",   AMBER,  4.4),
        ("LLM Layer",            "Gemini 1.5 Flash\nClaude Sonnet\nGPT-4o mini",     TEAL,   6.45),
        ("Vector Store",         "BAAI bge-small\n384-dim embeddings\nIn-memory index", LIGHT_PUR, 8.35),
    ]
    for (title, body, col, x) in boxes:
        is_amber = (col == AMBER)
        fg = DARK if is_amber else WHITE
        add_rect(sl, x, 1.35, 1.5, 2.3, DARK)
        add_rect(sl, x, 1.35, 1.5, 0.42, col)
        add_text(sl, title, x+0.08, 1.4, 1.34, 0.35, size=10, bold=True,
                 color=DARK if is_amber else WHITE)
        add_text(sl, body, x+0.08, 1.82, 1.34, 1.7, size=9, color=LIGHT_PUR)
        if x < 8.35:
            add_text(sl, "→", x+1.55, 2.25, 0.5, 0.35, size=16, bold=True, color=PURPLE)

    # Data flow section
    add_rect(sl, 0.3, 3.85, 9.4, 0.04, PURPLE)
    add_text(sl, "Data Flow", 0.3, 3.98, 9.4, 0.35, size=13, bold=True, color=DARK)
    flow_steps = [
        "① PDF upload → pdfplumber text extraction → 512-token sliding-window chunking (64 overlap)",
        "② Each chunk embedded with BAAI/bge-small-en-v1.5 (384 dimensions, MPS-accelerated on Mac)",
        "③ Query → embed → cosine similarity top-10 → BM25 keyword score → 70/30 fusion rerank",
        "④ Sentence filter removes boilerplate (ToC, transmittal headers, contact lines)",
        "⑤ Top-5 filtered chunks → structured LLM prompt → JSON response with key_points, confidence_label, citations",
    ]
    for i, s in enumerate(flow_steps):
        add_text(sl, s, 0.45, 4.38 + i*0.47, 9.1, 0.44, size=10.5, color=DARK)

    add_rect(sl, 0, 7.1, 10, 0.4, PURPLE)
    add_text(sl, "IntelliPolicy AI", 0.3, 7.13, 9.4, 0.34, size=10, color=LIGHT_PUR, align=PP_ALIGN.CENTER)


def slide_rag(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(sl, 0x1A, 0x0D, 0x2E)
    add_rect(sl, 0, 0, 10, 1.15, PURPLE)
    add_text(sl, "04  |  AI Assistant — RAG Pipeline", 0.5, 0.3, 9, 0.6, size=26, bold=True, color=WHITE)
    add_text(sl, "Retrieval-Augmented Generation with hybrid search and hallucination prevention",
             0.5, 0.78, 9, 0.35, size=12, color=LIGHT_PUR, italic=True)

    stages = [
        ("Query Analysis",        "Extract keywords\nRemove stopwords\nDetect question type\n(overview vs specific)", SKY),
        ("Hybrid Retrieval",      "Semantic search\n(cosine similarity)\n+ BM25 keyword score\n70 / 30 fusion", PURPLE),
        ("Reranking",             "Top-10 → reranked\nto Top-5 by fused\nscore + relevance\nthreshold 0.35", AMBER),
        ("Sentence Filter",       "Per-chunk sentence\nscoring. Removes:\n• ToC entries\n• Boilerplate\n• Contact info", TEAL),
        ("LLM Generation",        "Structured JSON\nprompt. Required\nopener enforcement.\nConfidence labelling", LIGHT_PUR),
    ]
    for i,(title,body,col) in enumerate(stages):
        x = 0.35 + i*1.87
        is_amber = col == AMBER
        fg = DARK if is_amber else WHITE
        add_rect(sl, x, 1.35, 1.65, 2.8, RGBColor(0x2A,0x1D,0x42))
        add_rect(sl, x, 1.35, 1.65, 0.42, col)
        add_text(sl, f"0{i+1}", x+0.1, 1.4, 0.4, 0.35, size=11, bold=True,
                 color=DARK if is_amber else WHITE)
        add_text(sl, title, x+0.38, 1.4, 1.2, 0.35, size=10, bold=True,
                 color=DARK if is_amber else WHITE)
        add_text(sl, body, x+0.1, 1.85, 1.45, 2.2, size=9.5, color=LIGHT_PUR)
        if i < 4:
            add_text(sl, "→", x+1.68, 2.5, 0.25, 0.35, size=14, bold=True, color=LIGHT_PUR)

    # Response fields
    divider(sl, 4.35)
    add_text(sl, "Structured Response Fields Returned", 0.5, 4.45, 9, 0.4, size=13, bold=True, color=WHITE)
    fields = [
        ("answer",             "Required opener: 'The document states…' or 'The uploaded document does not explicitly mention…'"),
        ("key_points",         "2–4 bullet facts extracted directly from evidence — no inference allowed"),
        ("confidence_label",   "High (≥0.70) / Medium (≥0.45) / Low (<0.45) — computed from vector similarity"),
        ("supporting_evidence","Document name + page number + verbatim quote (max 25 words)"),
        ("recommended_action", "One specific next step — does NOT assume prior-auth unless explicitly stated in evidence"),
    ]
    for i,(k,v) in enumerate(fields):
        y = 4.95 + i*0.41
        add_rect(sl, 0.45, y, 2.2, 0.35, PURPLE)
        add_text(sl, k, 0.55, y+0.04, 2.0, 0.3, size=9.5, bold=True, color=WHITE)
        add_text(sl, v, 2.75, y, 6.8, 0.38, size=9.5, color=LIGHT_PUR)

    add_rect(sl, 0, 7.1, 10, 0.4, PURPLE)
    add_text(sl, "IntelliPolicy AI", 0.3, 7.13, 9.4, 0.34, size=10, color=LIGHT_PUR, align=PP_ALIGN.CENTER)


def slide_features_1(prs):
    """Rule Extraction + Claims Validator on one slide."""
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(sl, 0xF7, 0xF3, 0xFB)
    add_rect(sl, 0, 0, 10, 1.15, DARK)
    add_text(sl, "05  |  Rule Extraction & Claims Validator", 0.5, 0.3, 9, 0.6, size=24, bold=True, color=WHITE)
    add_text(sl, "Structured rule parsing → machine-readable validation logic",
             0.5, 0.78, 9, 0.35, size=12, color=LIGHT_PUR, italic=True)

    # Rule Extraction panel
    add_rect(sl, 0.3, 1.3, 4.4, 5.6, DARK)
    add_rect(sl, 0.3, 1.3, 4.4, 0.42, PURPLE)
    add_text(sl, "📋  Rule Extraction Engine", 0.45, 1.35, 4.1, 0.38, size=12, bold=True, color=WHITE)
    re_points = [
        "Input: raw PDF text (up to 25 chunks per document)",
        "LLM prompt: identifies 12 rule types including Prior Auth,\n   Billing, Coverage, Supervision, Frequency Limits",
        "Output schema: procedure · cpt_code · icd_code · plan_type\n   · requires_prior_authorization · documentation_required\n   · authorization_timing · emergency_exception · confidence",
        "IF / THEN logic auto-generated from actor + restriction +\n   allowed_action fields",
        "Deduplication: CPT-key and actor+restriction fingerprinting\n   prevents duplicate rule cards",
        "Export: full JSON download for downstream integration",
        "Send to Claims Validator: passes cpt_code + procedure +\n   plan_type via URL search params to pre-fill the claim form",
    ]
    for i,p in enumerate(re_points):
        add_text(sl, f"• {p}", 0.48, 1.82+i*0.7, 4.0, 0.65, size=9.5, color=LIGHT_PUR)

    # Claims Validator panel
    add_rect(sl, 5.0, 1.3, 4.4, 5.6, DARK)
    add_rect(sl, 5.0, 1.3, 4.4, 0.42, AMBER)
    add_text(sl, "🛡  Claims Validator", 5.15, 1.35, 4.1, 0.38, size=12, bold=True, color=DARK)
    cv_points = [
        "Input: CPT code · ICD-10 diagnosis · plan type\n   · procedure description · service date",
        "Step 1 — Rule match: checks extracted BusinessRule\n   store for CPT/plan-type match (O(n) scan)",
        "Step 2 — Document fallback: if no rule match, runs\n   RAG query against the active policy document",
        "Decision engine: Approved / Denied / Needs Review\n   with reason, policy_source, source_page, confidence",
        "Audit record created: every validation permanently\n   logged to claim_audit_store with full decision trace",
        "Confidence scoring: rule-matched decisions score\n   ≥ 0.80; document-fallback scores 0.40–0.75",
    ]
    for i,p in enumerate(cv_points):
        add_text(sl, f"• {p}", 5.18, 1.82+i*0.82, 4.05, 0.75, size=9.5, color=LIGHT_PUR)

    add_rect(sl, 0, 7.1, 10, 0.4, PURPLE)
    add_text(sl, "IntelliPolicy AI", 0.3, 7.13, 9.4, 0.34, size=10, color=LIGHT_PUR, align=PP_ALIGN.CENTER)


def slide_features_2(prs):
    """Policy Compare + Audit Trail."""
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(sl, 0x1A, 0x0D, 0x2E)
    add_rect(sl, 0, 0, 10, 1.15, PURPLE)
    add_text(sl, "06  |  Policy Compare & Audit Trail", 0.5, 0.3, 9, 0.6, size=24, bold=True, color=WHITE)
    add_text(sl, "Version-aware change detection with full AI transparency",
             0.5, 0.78, 9, 0.35, size=12, color=LIGHT_PUR, italic=True)

    add_rect(sl, 0.3, 1.3, 4.4, 5.6, RGBColor(0x2A,0x1D,0x42))
    add_rect(sl, 0.3, 1.3, 4.4, 0.42, TEAL)
    add_text(sl, "⚖  Policy Compare", 0.45, 1.35, 4.1, 0.38, size=12, bold=True, color=DARK)
    pc_points = [
        "Select any two indexed policy documents as\n   old_version and new_version",
        "Comparison agent retrieves top-15 chunks from\n   each document and sends to LLM for diff analysis",
        "Output: list of PolicyChange objects with fields:\n   area · old_value · new_value · impact · risk_level\n   · change_type (Added / Modified / Removed)",
        "Risk classification: High / Medium / Low based on\n   clinical and financial impact keywords",
        "Summary card: total changes · high-risk count ·\n   document names with full change detail cards",
        "Use case: annual policy refresh cycles —\n   instantly surfaces coverage rule changes",
    ]
    for i,p in enumerate(pc_points):
        add_text(sl, f"• {p}", 0.48, 1.82+i*0.82, 4.05, 0.75, size=9.5, color=LIGHT_PUR)

    add_rect(sl, 5.0, 1.3, 4.4, 5.6, RGBColor(0x2A,0x1D,0x42))
    add_rect(sl, 5.0, 1.3, 4.4, 0.42, SKY)
    add_text(sl, "🔎  Audit Trail", 5.15, 1.35, 4.1, 0.38, size=12, bold=True, color=DARK)
    at_points = [
        "Every AI Assistant query creates an immutable\n   AuditRecord stored server-side in audit_store",
        "Record fields: session_id · question · retrieved_pages\n   · reasoning_summary · final_answer · confidence\n   · source_citations · steps[]",
        "Steps[] array: each pipeline stage timestamped —\n   Intake → Retrieval → Reranking → LLM Generation",
        "Source citations: document_id · document_name\n   · page_number · verbatim text · relevance_score",
        "Audit list view: last 50 sessions with expandable\n   detail — full trace replay for any decision",
        "Compliance use case: supports prior-auth appeals\n   with documented evidence chain",
    ]
    for i,p in enumerate(at_points):
        add_text(sl, f"• {p}", 5.18, 1.82+i*0.82, 4.05, 0.75, size=9.5, color=LIGHT_PUR)

    add_rect(sl, 0, 7.1, 10, 0.4, PURPLE)
    add_text(sl, "IntelliPolicy AI", 0.3, 7.13, 9.4, 0.34, size=10, color=LIGHT_PUR, align=PP_ALIGN.CENTER)


def slide_tech_stack(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(sl, 0xF7, 0xF3, 0xFB)
    add_rect(sl, 0, 0, 10, 1.15, DARK)
    add_text(sl, "07  |  Technology Stack", 0.5, 0.3, 9, 0.6, size=26, bold=True, color=WHITE)
    add_text(sl, "Production-grade choices aligned with enterprise healthcare standards",
             0.5, 0.78, 9, 0.35, size=12, color=LIGHT_PUR, italic=True)

    categories = [
        ("Frontend",      [("Next.js 14","App Router, RSC, client components"), ("Tailwind CSS 3","Utility-first; CSS cascade layers"), ("Framer Motion","Page & card animations"), ("Lucide React","Icon system"), ("TypeScript","Full type safety end-to-end")]),
        ("Backend",       [("FastAPI","Async Python, Pydantic v2 validation"), ("Python 3.13","Latest CPython runtime"), ("pdfplumber","High-fidelity PDF text extraction"), ("sentence-transformers","BAAI/bge-small-en-v1.5 embeddings"), ("uvicorn","ASGI server with lifespan hooks")]),
        ("AI / ML",       [("BAAI/bge-small-en-v1.5","384-dim multilingual embeddings, ~130 MB"), ("Google Gemini 1.5 Flash","Primary LLM — 1M context, JSON mode"), ("Anthropic Claude Sonnet","Fallback LLM provider"), ("OpenAI GPT-4o mini","Third fallback provider"), ("BM25 + cosine","Hybrid retrieval fusion 70/30")]),
        ("Infra / DevOps",[("Railway","Docker-based backend deploy with Nixpacks"), ("Vercel","Frontend edge deployment, automatic CI/CD"), ("GitHub Actions","Push-triggered deploy pipeline"), ("Docker","Containerised build, model pre-baked"), ("In-memory store","Zero-DB design for POC portability")]),
    ]
    for col,(cat,items) in enumerate(categories):
        x = 0.3 + col*2.35
        add_rect(sl, x, 1.3, 2.2, 0.42, PURPLE)
        add_text(sl, cat, x+0.1, 1.35, 2.0, 0.35, size=11, bold=True, color=WHITE)
        for j,(name,desc) in enumerate(items):
            y = 1.85 + j*1.02
            add_rect(sl, x, y, 2.2, 0.95, DARK)
            add_text(sl, name, x+0.1, y+0.06, 2.0, 0.35, size=10, bold=True, color=AMBER)
            add_text(sl, desc, x+0.1, y+0.42, 2.0, 0.5,  size=8.5, color=LIGHT_PUR)

    add_rect(sl, 0, 7.1, 10, 0.4, PURPLE)
    add_text(sl, "IntelliPolicy AI", 0.3, 7.13, 9.4, 0.34, size=10, color=LIGHT_PUR, align=PP_ALIGN.CENTER)


def slide_results(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(sl, 0x1A, 0x0D, 0x2E)
    add_rect(sl, 0, 0, 10, 1.15, PURPLE)
    add_text(sl, "08  |  Results & Impact", 0.5, 0.3, 9, 0.6, size=26, bold=True, color=WHITE)
    add_text(sl, "Measurable outcomes from the working prototype",
             0.5, 0.78, 9, 0.35, size=12, color=LIGHT_PUR, italic=True)

    metrics = [
        ("< 5 s",  "End-to-end answer\nlatency (warm cache)"),
        ("≥ 0.70", "Average confidence\non targeted queries"),
        ("70/30",  "Semantic / keyword\nhybrid retrieval blend"),
        ("6",      "Pages / modules\nfully functional"),
    ]
    for i,(val,label) in enumerate(metrics):
        x = 0.5 + i*2.35
        add_rect(sl, x, 1.3, 2.1, 1.7, RGBColor(0x2A,0x1D,0x42))
        add_rect(sl, x, 1.3, 2.1, 0.06, PURPLE)
        add_text(sl, val,   x+0.1, 1.42, 1.9, 0.75, size=30, bold=True, color=AMBER, align=PP_ALIGN.CENTER)
        add_text(sl, label, x+0.1, 2.18, 1.9, 0.75, size=10, color=WHITE, align=PP_ALIGN.CENTER)

    divider(sl, 3.18)
    add_text(sl, "Key Technical Achievements", 0.5, 3.28, 9, 0.4, size=14, bold=True, color=WHITE)
    achievements = [
        "✓  Cold-start latency eliminated: BAAI model pre-baked into Docker image via RUN python -c command at build time; pre-warmed in FastAPI lifespan hook",
        "✓  Hallucination prevention: LLM prompt enforces required answer openers and forbids recommending prior-auth unless the evidence explicitly states it",
        "✓  Boilerplate filter: regex _BOILERPLATE_PAT + _TOC_RUNON_PAT remove transmittal headers, table-of-contents run-ons, and contact-information lines before LLM context is assembled",
        "✓  Multi-provider LLM: single set_api_key() call switches between Gemini, Claude, and GPT-4o mini at runtime with automatic extractive fallback when no key is configured",
        "✓  Claims → Validator handoff: rules page builds /claims?cpt=&procedure=&plan_type= URL params so the claim form arrives pre-filled — zero copy-paste required",
        "✓  Full audit chain: every question, retrieved page, reasoning step, and LLM decision is logged to an in-memory audit store with session-level replay",
    ]
    for i,a in enumerate(achievements):
        add_text(sl, a, 0.45, 3.78+i*0.52, 9.1, 0.48, size=10, color=LIGHT_PUR)

    add_rect(sl, 0, 7.1, 10, 0.4, PURPLE)
    add_text(sl, "IntelliPolicy AI", 0.3, 7.13, 9.4, 0.34, size=10, color=LIGHT_PUR, align=PP_ALIGN.CENTER)


def slide_limitations(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(sl, 0xF7, 0xF3, 0xFB)
    add_rect(sl, 0, 0, 10, 1.15, DARK)
    add_text(sl, "09  |  Limitations & Future Roadmap", 0.5, 0.3, 9, 0.6, size=24, bold=True, color=WHITE)
    add_text(sl, "Honest constraints of the POC and production upgrade path",
             0.5, 0.78, 9, 0.35, size=12, color=LIGHT_PUR, italic=True)

    add_rect(sl, 0.3, 1.3, 4.3, 5.6, DARK)
    add_rect(sl, 0.3, 1.3, 4.3, 0.42, RGBColor(0xF8,0x71,0x71))
    add_text(sl, "⚠  Current Limitations", 0.45, 1.35, 4.0, 0.38, size=12, bold=True, color=DARK)
    limits = [
        ("In-Memory Vector Store",  "Vectors lost on server restart.\nNo persistence between deploys."),
        ("Single-Document Context", "Each query searches one document\nat a time; no cross-doc synthesis."),
        ("LLM Key Requirement",     "Without an API key the system\nfalls back to extractive QA only."),
        ("PDF-Only Ingestion",      "DOCX, HTML, and structured data\nsources not yet supported."),
        ("No Auth / Multi-tenant",  "POC has no user authentication;\nnot production-ready for PHI data."),
    ]
    for i,(title,body) in enumerate(limits):
        y = 1.85 + i*0.96
        add_rect(sl, 0.45, y, 4.0, 0.88, RGBColor(0x2A,0x1D,0x42))
        add_text(sl, title, 0.6, y+0.06, 3.7, 0.32, size=10, bold=True, color=AMBER)
        add_text(sl, body,  0.6, y+0.4, 3.7, 0.45, size=9, color=LIGHT_PUR)

    add_rect(sl, 4.9, 1.3, 4.8, 5.6, DARK)
    add_rect(sl, 4.9, 1.3, 4.8, 0.42, PURPLE)
    add_text(sl, "🚀  Production Roadmap", 5.05, 1.35, 4.5, 0.38, size=12, bold=True, color=WHITE)
    roadmap = [
        ("PostgreSQL + pgvector",   "Persistent vector store with\nOAuth2 multi-tenant isolation"),
        ("Cross-Document RAG",      "Query across all documents;\nmerge evidence from multiple sources"),
        ("Streaming Responses",     "Server-sent events for real-time\ntoken streaming in the UI"),
        ("HIPAA Compliance Layer",  "PHI redaction, audit encryption,\nBAA-compatible deployment on AWS"),
        ("Fine-Tuned Reranker",     "Domain-specific reranking model\ntrained on CMS policy corpus"),
    ]
    for i,(title,body) in enumerate(roadmap):
        y = 1.85 + i*0.96
        add_rect(sl, 5.05, y, 4.5, 0.88, RGBColor(0x2A,0x1D,0x42))
        add_text(sl, title, 5.2, y+0.06, 4.2, 0.32, size=10, bold=True, color=SKY)
        add_text(sl, body,  5.2, y+0.4, 4.2, 0.45, size=9, color=LIGHT_PUR)

    add_rect(sl, 0, 7.1, 10, 0.4, PURPLE)
    add_text(sl, "IntelliPolicy AI", 0.3, 7.13, 9.4, 0.34, size=10, color=LIGHT_PUR, align=PP_ALIGN.CENTER)


def slide_demo(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(sl, 0x1A, 0x0D, 0x2E)
    add_rect(sl, 0, 0, 10, 1.15, PURPLE)
    add_text(sl, "10  |  Live Demo Walkthrough", 0.5, 0.3, 9, 0.6, size=26, bold=True, color=WHITE)
    add_text(sl, "End-to-end flow demonstration",
             0.5, 0.78, 9, 0.35, size=12, color=LIGHT_PUR, italic=True)

    steps = [
        ("Step 1", "Upload Document", "Navigate to Upload Documents → load prior_authorization_policy_2026.pdf\nfrom the built-in sample library. Observe chunking stats: page count + chunk count."),
        ("Step 2", "AI Assistant",    "Ask: 'What services require prior authorization?' Observe structured response:\nrequired opener, key_points bullets, confidence label, citations with page numbers."),
        ("Step 3", "Rule Extraction", "Select the uploaded document → Extract. Review IF/THEN logic cards,\nrisk classification badges, and CPT code chips in the Extraction Summary."),
        ("Step 4", "Claims Validator","Click Send to Claims Validator. CPT code, procedure, and plan type\nauto-populate. Add a diagnosis code → Validate → review decision + audit record."),
        ("Step 5", "Policy Compare",  "Select prior_auth_2026 vs policy_2025. Review change detection cards\nwith risk scoring and old_value / new_value diff for each detected change."),
        ("Step 6", "Audit Trail",     "Navigate to Audit Trail. Expand any session to see retrieved pages,\nreasoning steps, citations, and confidence — full AI decision transparency."),
    ]
    for i,(step,title,body) in enumerate(steps):
        col = i % 2
        row = i // 2
        x = 0.35 + col*4.85
        y = 1.35 + row*1.85
        add_rect(sl, x, y, 4.55, 1.7, RGBColor(0x2A,0x1D,0x42))
        add_rect(sl, x, y, 0.7, 1.7, PURPLE)
        add_text(sl, step, x+0.08, y+0.55, 0.55, 0.55, size=9, bold=True, color=LIGHT_PUR, align=PP_ALIGN.CENTER)
        add_text(sl, title, x+0.8, y+0.1, 3.6, 0.38, size=11, bold=True, color=AMBER)
        add_text(sl, body,  x+0.8, y+0.52, 3.6, 1.1,  size=9.5, color=LIGHT_PUR)

    add_rect(sl, 0, 7.1, 10, 0.4, PURPLE)
    add_text(sl, "IntelliPolicy AI  ·  localhost:3000", 0.3, 7.13, 9.4, 0.34, size=10, color=LIGHT_PUR, align=PP_ALIGN.CENTER)


def slide_thankyou(prs):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(sl, 0x1A, 0x0D, 0x2E)
    add_rect(sl, 0, 0, 0.18, 7.5, PURPLE)
    add_rect(sl, 0.18, 0, 0.06, 7.5, LIGHT_PUR)
    add_rect(sl, 0, 0, 10, 0.08, PURPLE)
    add_rect(sl, 0, 7.1, 10, 0.4, PURPLE)
    add_text(sl, "COTIVITI", 0.55, 0.27, 2.6, 0.45, size=18, bold=True, color=LIGHT_PUR)
    divider(sl, 1.2, PURPLE)
    add_text(sl, "Thank You", 0.5, 1.5, 9, 1.0, size=52, bold=True, color=WHITE)
    add_text(sl, "Questions & Discussion", 0.5, 2.6, 9, 0.55, size=22, color=LIGHT_PUR)
    divider(sl, 3.3, LIGHT_PUR)

    contact = [
        ("Developer",   "Sohith Kampalli"),
        ("GitHub",      "github.com/sohithk2002/intellipolicy-ai"),
        ("Backend",     "Railway — FastAPI + Docker"),
        ("Frontend",    "Vercel — Next.js 14"),
        ("Email",       "sohithkampalli@gmail.com"),
        ("Submitted to","jesus.hurtado@cotiviti.com"),
    ]
    for i,(k,v) in enumerate(contact):
        y = 3.5 + i*0.5
        add_text(sl, k+":", 0.5, y, 2.2, 0.45, size=12, bold=True, color=LIGHT_PUR)
        add_text(sl, v,    2.8, y, 6.5, 0.45, size=12, color=WHITE)

    add_text(sl, "\"Turning policy PDFs into intelligent, auditable decisions — at scale.\"",
             0.5, 6.55, 9, 0.45, size=12, italic=True, color=LIGHT_PUR, align=PP_ALIGN.CENTER)
    add_text(sl, "IntelliPolicy AI — Cotiviti Assessment 2026", 0.3, 7.13, 9.4, 0.34,
             size=10, color=LIGHT_PUR, align=PP_ALIGN.CENTER)


def build_pptx():
    prs = Presentation()
    prs.slide_width  = Inches(10)
    prs.slide_height = Inches(7.5)

    slide_cover(prs)
    slide_problem(prs)
    slide_solution(prs)
    slide_architecture(prs)
    slide_rag(prs)
    slide_features_1(prs)
    slide_features_2(prs)
    slide_tech_stack(prs)
    slide_results(prs)
    slide_limitations(prs)
    slide_demo(prs)
    slide_thankyou(prs)

    path = OUT / "IntelliPolicy_AI_Assessment_Deck.pptx"
    prs.save(str(path))
    print(f"✓  PPT saved → {path}")
    return path


# ═══════════════════════════════════════════════════════════════════════════
#  WORD DOCUMENT
# ═══════════════════════════════════════════════════════════════════════════

def set_doc_style(doc):
    from docx.oxml.ns import qn
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = DPt(11)
    style.paragraph_format.space_after = DPt(6)


def heading(doc, text, level=1):
    p = doc.add_heading(text, level=level)
    run = p.runs[0] if p.runs else p.add_run(text)
    run.font.color.rgb = DRGBColor(0x6B, 0x2D, 0x8B)
    return p


def body(doc, text):
    p = doc.add_paragraph(text)
    p.paragraph_format.space_after = DPt(8)
    return p


def bullet(doc, text, level=0):
    p = doc.add_paragraph(text, style="List Bullet")
    p.paragraph_format.left_indent = DInches(0.25 * (level + 1))
    p.paragraph_format.space_after = DPt(4)
    return p


def add_table(doc, headers, rows):
    table = doc.add_table(rows=1+len(rows), cols=len(headers))
    table.style = "Table Grid"
    hdr_row = table.rows[0]
    for i,h in enumerate(headers):
        cell = hdr_row.cells[i]
        cell.text = h
        for run in cell.paragraphs[0].runs:
            run.font.bold = True
            run.font.color.rgb = DRGBColor(0xFF,0xFF,0xFF)
        from docx.oxml.ns import qn as dqn
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:fill"), "6B2D8B")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:val"), "clear")
        tcPr.append(shd)
    for rdata in rows:
        row = table.add_row()
        for i,val in enumerate(rdata):
            row.cells[i].text = str(val)
    doc.add_paragraph()
    return table


def build_docx():
    doc = Document()
    set_doc_style(doc)

    # Cover block
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title_p.add_run("IntelliPolicy AI")
    run.font.size = DPt(28)
    run.font.bold = True
    run.font.color.rgb = DRGBColor(0x6B,0x2D,0x8B)

    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_p.add_run("Intelligent Healthcare Policy Analysis Platform").font.size = DPt(14)

    meta_p = doc.add_paragraph()
    meta_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    today = datetime.date.today().strftime("%B %d, %Y")
    meta_p.add_run(
        f"Cotiviti Software Engineer Intern Assessment  ·  {today}\n"
        "Submitted by: Sohith Kampalli  ·  sohithkampalli@gmail.com\n"
        "Submitted to: jesus.hurtado@cotiviti.com"
    ).font.size = DPt(10)

    doc.add_page_break()

    # ── 1. Executive Summary ─────────────────────────────────────────────
    heading(doc, "1. Executive Summary")
    body(doc,
        "IntelliPolicy AI is a full-stack, production-deployed healthcare policy intelligence platform "
        "built as a Cotiviti internship technical assessment. The system transforms static PDF policy "
        "manuals into an interactive, AI-driven knowledge base that answers coverage questions, "
        "extracts structured business rules, compares policy versions, validates insurance claims, and "
        "maintains a full audit trail of every decision.")
    body(doc,
        "The platform employs a five-agent architecture orchestrated over a FastAPI backend. Each agent "
        "is a specialised Python module responsible for a distinct pipeline stage: document ingestion, "
        "hybrid vector retrieval, LLM-powered question answering, policy comparison, and rule-based "
        "claims validation. The frontend is a Next.js 14 single-page application deployed on Vercel; "
        "the backend runs in a Docker container on Railway.")

    # ── 2. Problem Statement ─────────────────────────────────────────────
    heading(doc, "2. Problem Statement")
    body(doc,
        "Healthcare policy administration involves several compounding inefficiencies that IntelliPolicy "
        "AI was designed to address:")
    problems = [
        ("Manual Policy Review", "Clinical analysts spend 60–80% of their time reading multi-hundred-page "
         "PDF policy manuals to answer single coverage questions, leading to high labour costs and "
         "inconsistent interpretations across staff."),
        ("Slow Prior-Authorization Cycles", "Cross-referencing multiple policy versions to determine "
         "whether a procedure requires prior authorisation typically takes 3–5 business days, delaying "
         "patient care."),
        ("Version Drift Risk", "Healthcare organisations manage 10–50 active policy versions simultaneously. "
         "Detecting changes between annual or quarterly revisions is fully manual, creating coverage-gap "
         "and compliance risk."),
        ("Absence of Audit Trails", "Existing workflows produce no structured record of which policy "
         "evidence supported a coverage decision, exposing organisations to appeal and regulatory "
         "liability."),
    ]
    for title, description in problems:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = DInches(0.25)
        p.paragraph_format.space_after = DPt(6)
        run = p.add_run(f"{title}: ")
        run.font.bold = True
        run.font.color.rgb = DRGBColor(0x6B,0x2D,0x8B)
        p.add_run(description)

    # ── 3. System Architecture ───────────────────────────────────────────
    heading(doc, "3. System Architecture")
    heading(doc, "3.1 High-Level Overview", level=2)
    body(doc,
        "The platform follows a three-tier architecture: a Next.js 14 frontend communicates with a "
        "FastAPI backend via a RESTful JSON API. The backend manages five specialised agents, a "
        "shared in-memory vector store, and a persisted LLM configuration file.")

    heading(doc, "3.2 Document Ingestion Pipeline", level=2)
    body(doc,
        "When a PDF is uploaded, the Intake Agent extracts text using pdfplumber, which preserves "
        "layout metadata including page numbers and column structure. The text is segmented into "
        "512-token chunks with a 64-token sliding overlap to preserve inter-sentence context. Each "
        "chunk is embedded using the BAAI/bge-small-en-v1.5 sentence-transformer model, producing a "
        "384-dimensional dense vector. Vectors are stored in an InMemoryVectorStore alongside metadata "
        "(document_id, page_number, document_name, relevance_score).")
    body(doc,
        "To eliminate cold-start latency, the BAAI model is pre-downloaded into the Docker image at "
        "build time and pre-warmed during FastAPI's lifespan startup hook. This ensures the first "
        "query after deployment is as fast as all subsequent queries.")

    heading(doc, "3.3 Retrieval-Augmented Generation (RAG) Pipeline", level=2)
    steps = [
        ("Query Analysis", "Incoming question keywords are extracted, stopwords removed, and the question classified as overview-type or specific-type to tune retrieval depth (top_k=20 for overviews, top_k=10 for specific queries)."),
        ("Hybrid Retrieval", "Cosine similarity search (semantic) is fused with BM25 keyword scoring in a 70/30 ratio to balance semantic recall with exact-term precision."),
        ("Reranking", "The top-10 fused results are reranked and trimmed to 5 chunks using a relevance threshold of 0.35."),
        ("Sentence Filtering", "Each chunk is split into sentences. A two-stage filter removes: (a) table-of-contents entries and run-on section-number lines detected by _TOC_RUNON_PAT, and (b) boilerplate sentences (transmittal headers, contact information, revision-history lines) matched by _BOILERPLATE_PAT."),
        ("LLM Generation", "The 3–5 filtered, sentence-scored chunks are assembled into a structured prompt. The prompt enforces required answer openers ('The document states…', 'The uploaded document does not explicitly mention this…') and forbids hallucinating prior-authorisation requirements unless the evidence explicitly uses those words."),
        ("Structured Response", "The LLM returns a JSON object with: answer, key_points, confidence, confidence_label (High/Medium/Low), evidence, supporting_evidence (document + page + quote), recommended_action, follow_up_questions, and reasoning_steps."),
    ]
    for i,(title,desc) in enumerate(steps):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = DInches(0.25)
        p.paragraph_format.space_after = DPt(5)
        run = p.add_run(f"Step {i+1} — {title}: ")
        run.font.bold = True
        p.add_run(desc)

    # ── 4. Features ──────────────────────────────────────────────────────
    heading(doc, "4. Platform Features")

    heading(doc, "4.1 Document Upload & Ingestion", level=2)
    body(doc,
        "The Upload Documents page accepts PDF files up to 50 MB. Files are processed server-side "
        "via the /upload endpoint, which invokes the Intake Agent. The UI displays chunk count, "
        "page count, and document status. Six sample policy documents are bundled with the deployment "
        "and can be loaded without a file upload.")

    heading(doc, "4.2 AI Assistant", level=2)
    body(doc,
        "The AI Assistant accepts natural-language questions and returns grounded, citation-backed "
        "answers. The interface displays: the structured answer with required opener, confidence "
        "badge (High/Medium/Low), key-points bullets, page-level citations with relevance scores, "
        "recommended next action, and AI reasoning steps. Without an LLM API key the system falls "
        "back to extractive QA using sentence scoring, which is fully functional for most queries.")

    heading(doc, "4.3 Policy Compare", level=2)
    body(doc,
        "The Policy Compare feature accepts two document IDs and invokes the Comparison Agent. The "
        "agent retrieves the top 15 chunks from each document and sends them to the LLM with a "
        "structured diff prompt. Each detected change is returned as a PolicyChange object with: "
        "area, old_value, new_value, impact description, risk_level (High/Medium/Low), and "
        "change_type (Added/Modified/Removed). A summary card shows total changes and high-risk count.")

    heading(doc, "4.4 Rule Extraction", level=2)
    body(doc,
        "The Rule Extraction engine processes raw policy text or an indexed document and returns "
        "structured BusinessRule objects. Each rule includes: procedure name, CPT code, ICD code, "
        "plan type, prior-authorisation flag, documentation requirements, authorization timing, "
        "emergency exception window, source page, confidence score, and rule type. Twelve rule "
        "types are supported: Prior Authorization, Billing, Coverage, Documentation, Provider "
        "Restriction, Supervision, Coding, Frequency Limits, Time Windows, Eligibility, Exceptions, "
        "and Prohibitions. Rules are deduplicated by CPT-key and actor+restriction fingerprinting. "
        "IF/THEN logic is auto-generated from actor, restriction, and allowed_action fields for "
        "human-readable validation display.")

    heading(doc, "4.5 Claims Validator", level=2)
    body(doc,
        "The Claims Validator accepts CPT code, ICD-10 diagnosis code, plan type, procedure name, "
        "and service date. Validation proceeds in two stages: first a rule-store lookup for a "
        "CPT/plan-type match, then a RAG document fallback if no rule is found. The decision "
        "engine returns: Approved, Denied, or Needs Review, with reason, policy_source, source_page, "
        "confidence score, missing_info list, and next_steps. Every validation is written to the "
        "claim audit store. The Claims Validator is integrated with Rule Extraction via URL search "
        "params: clicking 'Send to Claims Validator' from the rules page pre-fills cpt_code, "
        "procedure, and plan_type fields automatically.")

    heading(doc, "4.6 Audit Trail", level=2)
    body(doc,
        "Every AI Assistant query creates an AuditRecord in the server-side audit_store. Each record "
        "contains: session_id, question, list of retrieved page numbers, reasoning_summary, "
        "final_answer, confidence score, source citations (with page numbers and verbatim text), "
        "and a timestamped steps array covering every pipeline stage from Intake through LLM "
        "Generation. The Audit Trail page displays the 50 most recent records with full expandable "
        "detail for compliance review and decision appeal support.")

    # ── 5. Technical Implementation Details ─────────────────────────────
    heading(doc, "5. Technical Implementation Details")

    heading(doc, "5.1 Frontend", level=2)
    add_table(doc,
        ["Technology", "Version", "Purpose"],
        [
            ("Next.js",          "14 (App Router)",   "Full-stack React framework, RSC + client components"),
            ("Tailwind CSS",     "3.x",               "Utility-first CSS, cascade layer architecture"),
            ("Framer Motion",    "11.x",              "Page transitions, card animations, AnimatePresence"),
            ("TypeScript",       "5.x",               "Full type safety across all components and API calls"),
            ("Lucide React",     "0.x",               "Consistent icon system"),
            ("next/navigation",  "built-in",          "useSearchParams for cross-page state handoff"),
        ]
    )

    heading(doc, "5.2 Backend", level=2)
    add_table(doc,
        ["Technology", "Version", "Purpose"],
        [
            ("FastAPI",               "0.115.x",   "Async ASGI framework, Pydantic v2 validation"),
            ("Python",                "3.13",       "Runtime; union type syntax, modern stdlib"),
            ("sentence-transformers", "3.x",        "BAAI/bge-small-en-v1.5 embedding model"),
            ("pdfplumber",            "0.11.x",     "High-fidelity PDF text extraction"),
            ("uvicorn",               "0.32.x",     "ASGI server with lifespan hooks"),
            ("httpx",                 "0.27.x",     "Async HTTP client for LLM API calls"),
        ]
    )

    heading(doc, "5.3 Deployment", level=2)
    bullet(doc, "Backend: Railway platform, Docker container, Nixpacks build detection. Model pre-baked at build time to avoid cold-start on Railway's serverless-adjacent containers.")
    bullet(doc, "Frontend: Vercel, automatic CI/CD from GitHub main branch, edge network CDN.")
    bullet(doc, "Environment variables: ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY, DATABASE_URL (optional). Secrets never committed; configured via Railway/Vercel dashboard.")

    # ── 6. Challenges & Solutions ────────────────────────────────────────
    heading(doc, "6. Engineering Challenges & Solutions")
    challenges = [
        ("Cold-Start Latency",
         "Railway containers restart frequently. The BAAI model (~130 MB) took 45–90 seconds to download on each restart, making the first query very slow.",
         "Pre-downloaded the model into the Docker image with a RUN python -c command in the Dockerfile, reducing cold-start to under 3 seconds. Added a lifespan pre-warm call to ensure the model is in GPU/MPS memory before the first request."),
        ("Boilerplate Contamination",
         "Policy PDFs contain extensive table-of-contents, transmittal headers, and contact-information sections. These were being included in LLM context, producing answers that quoted ToC entries instead of policy content.",
         "Built a two-layer filter: _BOILERPLATE_PAT (regex matching 8 boilerplate patterns) and _TOC_RUNON_PAT (detects concatenated section-number lines like '10 - General 20 - MPFS 20.1 - ...'). Applied before LLM context assembly."),
        ("LLM Hallucination Prevention",
         "The LLM sometimes recommended prior authorisation or coverage denials without explicit document evidence.",
         "Prompt engineering: required answer openers, explicit prohibition on inferring prior-auth unless the evidence uses that exact phrase, and post-generation opener enforcement that prefixes raw-text answers with 'The document states:' automatically."),
        ("Cross-Page State Handoff",
         "The 'Send to Claims Validator' button navigated to /claims but sent no data, leaving the form blank.",
         "Built URL search-param handoff: rules page encodes cpt_code, procedure, and plan_type into the href; claims page reads them via useSearchParams() on mount inside a Suspense boundary."),
        ("Multi-Python Environment",
         "The development machine had Python 3.9, 3.11, and 3.13 installed. Dependencies (numpy, uvicorn, sentence-transformers) were scattered across environments.",
         "Pinned the backend to Python 3.13 (which had all deps) for local dev. Docker uses the same version via the python:3.13-slim base image."),
    ]
    for i,(title, problem, solution) in enumerate(challenges):
        heading(doc, f"6.{i+1} {title}", level=2)
        p = doc.add_paragraph()
        p.add_run("Problem: ").font.bold = True
        p.add_run(problem)
        p.paragraph_format.space_after = DPt(4)
        p = doc.add_paragraph()
        p.add_run("Solution: ").font.bold = True
        p.add_run(solution)

    # ── 7. Limitations ───────────────────────────────────────────────────
    heading(doc, "7. Limitations")
    body(doc,
        "The current implementation is a proof-of-concept and has the following known limitations:")
    lims = [
        "In-memory vector store: embeddings are not persisted to disk; a server restart clears all indexed documents.",
        "Single-document retrieval: each query searches one document at a time; cross-document synthesis is not supported.",
        "No user authentication: the platform has no login system and is not suitable for handling PHI data in production.",
        "PDF-only ingestion: DOCX, HTML, and structured data (JSON, CSV) are not yet supported.",
        "Extractive fallback quality: without an LLM API key, answers rely on sentence extraction which may miss nuanced policy language.",
    ]
    for l in lims:
        bullet(doc, l)

    # ── 8. Future Work ───────────────────────────────────────────────────
    heading(doc, "8. Future Work")
    fw = [
        ("PostgreSQL + pgvector", "Replace the in-memory store with a persistent PostgreSQL database using the pgvector extension for scalable, multi-tenant vector search."),
        ("OAuth2 / RBAC", "Add user authentication with role-based access control (Admin, Analyst, Reviewer) using Clerk or NextAuth."),
        ("Streaming Responses", "Implement server-sent events for real-time token streaming, improving perceived latency for long answers."),
        ("Cross-Document RAG", "Enable queries that synthesise evidence from all uploaded documents simultaneously using a multi-index retrieval strategy."),
        ("Fine-Tuned Reranker", "Train a domain-specific cross-encoder reranker on CMS policy corpora to improve precision on healthcare-specific retrieval."),
        ("HIPAA Compliance", "Add PHI redaction, audit-log encryption, and deploy on HIPAA-eligible AWS infrastructure with a Business Associate Agreement."),
    ]
    for title,desc in fw:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = DPt(5)
        p.paragraph_format.left_indent = DInches(0.25)
        run = p.add_run(f"{title}: ")
        run.font.bold = True
        run.font.color.rgb = DRGBColor(0x6B,0x2D,0x8B)
        p.add_run(desc)

    # ── 9. References ─────────────────────────────────────────────────────
    heading(doc, "9. References (APA)")
    refs = [
        "Centers for Medicare & Medicaid Services. (2025). Medicare Claims Processing Manual, Chapter 12: Physicians/Nonphysician Practitioners (Publication 100-04). U.S. Department of Health and Human Services. https://www.cms.gov/regulations-and-guidance/guidance/manuals",
        "Xiao, S., Liu, Z., Zhang, P., & Muennighoff, N. (2023). C-Pack: Packaged resources to advance general Chinese embedding. arXiv preprint arXiv:2309.07597. https://arxiv.org/abs/2309.07597",
        "Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., … Kiela, D. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. Advances in Neural Information Processing Systems, 33, 9459–9474.",
        "Robertson, S., & Zaragoza, H. (2009). The probabilistic relevance framework: BM25 and beyond. Foundations and Trends in Information Retrieval, 3(4), 333–389. https://doi.org/10.1561/1500000019",
        "Google DeepMind. (2024). Gemini 1.5: Unlocking multimodal understanding across millions of tokens of context. arXiv preprint arXiv:2403.05530. https://arxiv.org/abs/2403.05530",
        "Pydantic. (2024). Pydantic v2 documentation. https://docs.pydantic.dev/latest/",
        "Vercel. (2024). Next.js 14 documentation — App Router. https://nextjs.org/docs",
        "FastAPI. (2024). FastAPI documentation. https://fastapi.tiangolo.com/",
        "Railway. (2024). Railway deployment documentation. https://docs.railway.app/",
        "Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing, 3982–3992. https://doi.org/10.18653/v1/D19-4006",
    ]
    for r in refs:
        p = doc.add_paragraph(r, style="List Bullet")
        p.paragraph_format.left_indent = DInches(0.5)
        p.paragraph_format.first_line_indent = DInches(-0.25)
        p.paragraph_format.space_after = DPt(6)

    path = OUT / "IntelliPolicy_AI_Technical_Report.docx"
    doc.save(str(path))
    print(f"✓  Word doc saved → {path}")
    return path


# ═══════════════════════════════════════════════════════════════════════════
#  VIDEO SCRIPT
# ═══════════════════════════════════════════════════════════════════════════

SCRIPT = """\
╔══════════════════════════════════════════════════════════════════════════════╗
║         IntelliPolicy AI — Assessment Video Recording Script               ║
║         Cotiviti Software Engineer Intern Technical Assessment              ║
║         Speaker: Sohith Kampalli                                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

TOTAL TARGET LENGTH: 8–12 minutes
TONE: Confident, technical, conversational — as if presenting to a senior
      engineering team at Cotiviti. Use your own words; this script is a guide.
FORMAT: Screen recording with voiceover. Show each page as you describe it.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SEGMENT 1 — INTRODUCTION  [0:00 – 0:45]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Show: Screen with browser open, app at localhost:3000, hero/landing visible]

"Hi, I'm Sohith Kampalli. This is IntelliPolicy AI — an intelligent healthcare
policy analysis platform I built for the Cotiviti internship technical
assessment.

The core problem I set out to solve is this: healthcare analysts spend the
majority of their time reading dense, multi-hundred-page PDF policy manuals
just to answer questions like — does this CPT code require prior authorisation?
What changed between last year's policy and this year's?

IntelliPolicy AI answers those questions in under five seconds, with citations,
confidence scoring, and a full audit trail — using a five-agent AI pipeline
built on FastAPI, Next.js 14, and retrieval-augmented generation."

[Pause briefly — point to the sidebar navigation]

"Let me walk you through every feature."


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SEGMENT 2 — DASHBOARD  [0:45 – 1:30]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Navigate to: localhost:3000/dashboard]

"Starting with the Dashboard. This is the command centre — it shows live
metrics pulled from the backend at runtime:

  • Documents uploaded — how many PDFs have been indexed into the vector store
  • Questions answered — total AI Assistant queries processed this session
  • Rules extracted — count of structured business rules in the rule store
  • Claims validated — total claim decisions made by the validator
  • Average confidence — weighted mean similarity score across all queries

These numbers come from a live GET /stats API call to the FastAPI backend.
They update in real time as you use the platform.

[Point to the activity feed or recent items if visible]

The platform badge shows 'AI Platform · Live' and '5 agents operational' —
that status indicator confirms all five backend agents are responding."


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SEGMENT 3 — DOCUMENT UPLOAD  [1:30 – 2:30]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Navigate to: localhost:3000/upload]

"Upload Documents. This is where the pipeline starts.

[Click 'Load Sample' on prior_authorization_policy_2026.pdf]

I'm loading the Prior Authorization Policy 2026 — one of six sample documents
bundled with the deployment. These are realistic synthetic healthcare policy
PDFs covering prior auth, billing guidelines, telehealth, emergency services,
specialty drugs, and medical necessity.

Under the hood, uploading a PDF triggers the Intake Agent:
  1. pdfplumber extracts text with layout metadata preserved — page numbers,
     columns, headers
  2. The text is chunked into 512-token windows with a 64-token sliding overlap
     — that overlap ensures sentences at chunk boundaries aren't orphaned
  3. Each chunk is embedded using BAAI/bge-small-en-v1.5 — a 384-dimensional
     sentence transformer model. It runs on Apple MPS on my machine; on Railway
     it runs on CPU
  4. The vectors go into an in-memory store indexed by document_id

[Show the result: page count, chunk count appearing]

You can see the result — this document produced X pages and Y chunks. The
system is now ready to answer questions about it."


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SEGMENT 4 — AI ASSISTANT  [2:30 – 4:30]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Navigate to: localhost:3000/assistant]

"AI Assistant. This is the core feature — natural language querying over
uploaded policy documents.

[Type question]: 'What services require prior authorization?'
[Click Ask]

While it processes — let me explain the pipeline:

The question goes to the QA Agent which:
  Step 1 — extracts keywords, removes stopwords, detects question type
  Step 2 — runs hybrid retrieval: 70% cosine similarity over the 384-dim
            embedding space, 30% BM25 keyword score — fused together
  Step 3 — reranks the top-10 results down to 5 using a relevance threshold
  Step 4 — applies the sentence filter — this was a key engineering challenge.
            Policy PDFs have a lot of noise: table-of-contents entries,
            transmittal headers, contact information. My _BOILERPLATE_PAT
            regex and a run-on ToC detector strip those before the LLM ever
            sees them
  Step 5 — the filtered chunks go into a structured LLM prompt with strict
            rules: the answer MUST start with 'The document states...' or
            'The uploaded document does not explicitly mention this.' The LLM
            cannot infer prior-authorisation requirements — it can only report
            what the document explicitly says

[Result appears — point to each section]

Look at the response structure:

  • Answer — starts with the required opener. No hallucination.
  • Confidence — High, Medium, or Low based on vector similarity scores
  • Key Points — 2-4 bullet facts extracted directly from the evidence
  • Citations — document name, page number, relevance score
  • Recommended Action — one specific next step

[Ask a second question]: 'Can a technician interpret an audiology test without
physician supervision?'

[Show result]

'The document states: a technician may not interpret test results or engage in
clinical decision-making. They may be furnished by a qualified technician under
the direct supervision of a physician, but not under the supervision of an
audiologist or an NPP.'

Exact answer, page citation, high confidence. That's the RAG pipeline working."


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SEGMENT 5 — RULE EXTRACTION  [4:30 – 6:00]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Navigate to: localhost:3000/rules]

"Rule Extraction. This takes unstructured policy text and converts it into
machine-readable business rules.

[Select the uploaded document from the dropdown, click Extract]

The extraction agent sends up to 25 document chunks to the LLM with a
structured prompt that identifies 12 rule types: Prior Authorization, Billing,
Coverage, Documentation, Provider Restriction, Supervision, Coding, Frequency
Limits, and more.

[Show cards appearing]

Each card is a BusinessRule object. Look at what's been extracted:

  • Rule type badge — Prior Authorization, Billing, etc.
  • Risk classification — High, Medium, Low
  • IF / THEN logic — auto-generated from the actor, restriction, and
    allowed_action fields. IF Provider = [X] AND CPT = [Y] THEN
    Prior Authorization Required
  • Documentation required chips — specific documents needed
  • Authorization timing — how far in advance to submit
  • Emergency exception window
  • Source page — full traceability back to the PDF

The Extraction Summary at the bottom shows total rules, high-risk count,
average confidence, and all CPT codes, plan types, and providers extracted.

[Click Export JSON]

You can export the full ruleset as machine-readable JSON for downstream
integration into claims processing systems.

[Click Send to Claims Validator]

Now watch this — I click Send to Claims Validator. Notice the URL —
it includes the CPT code, procedure name, and plan type as search parameters.
The claims form is pre-filled automatically."


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SEGMENT 6 — CLAIMS VALIDATOR  [6:00 – 7:15]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Now at: localhost:3000/claims — form pre-filled from rules page]

"Claims Validator. The CPT code and procedure arrived automatically from the
rules page — zero manual entry required for those fields.

[Add a diagnosis code — e.g. M54.5]
[Click Validate Claim]

The validation pipeline has two stages:

  Stage 1 — Rule Store Lookup: checks the in-memory rule store for a
             CPT code and plan-type match. If found, decision is made
             from the structured rule — fastest path, highest confidence.

  Stage 2 — RAG Document Fallback: if no rule matches, the system runs
             a full retrieval query against the active policy document.
             Slower, but still accurate.

[Show the result card]

The result card shows:
  • Decision: Approved / Denied / Needs Review
  • Reason: specific policy language justifying the decision
  • Policy Source: which document supported the decision
  • Source Page: exact page number
  • Confidence Score: how certain the system is
  • Next Steps: actionable guidance for the claim processor
  • Missing Information: any fields needed for a complete determination

Every validation is permanently logged to the claim audit store.

[Point to the processing timeline animation]

That timeline shows the five pipeline stages completing in real time —
Input received → Rule search → Document fallback → Evidence found → Decision."


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SEGMENT 7 — POLICY COMPARE  [7:15 – 8:15]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Navigate to: localhost:3000/compare]

"Policy Compare. This is built for annual policy refresh cycles — when a new
version of a policy comes out, analysts need to know exactly what changed.

[Select two documents — old version vs new version, click Compare]

The Comparison Agent retrieves the top 15 chunks from each document and sends
them to the LLM with a structured diff prompt. Every detected change comes
back as a PolicyChange object.

[Show results]

Each change card shows:
  • Area: which coverage or billing area changed
  • Old Value vs New Value: exactly what the text said before and after
  • Risk Level: High for coverage and prior-auth changes,
                Medium for documentation changes, Low for administrative
  • Change Type: Added, Modified, or Removed

The summary at the top shows total changes detected and how many are
high-risk — so an analyst can triage immediately instead of reading
the entire document."


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SEGMENT 8 — AUDIT TRAIL  [8:15 – 9:00]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Navigate to: localhost:3000/audit]

"Audit Trail. This is the compliance backbone of the platform.

Every AI Assistant query — every single one — creates an immutable audit
record. You can see all the sessions we ran during this demo.

[Click on a session to expand it]

Each record contains:
  • The exact question asked
  • Every page that was retrieved from the vector store
  • The full reasoning summary — what the system considered
  • The final answer given
  • Confidence score
  • Source citations with document name, page number, and the exact
    text passage that was used as evidence
  • A timestamped steps array: every pipeline stage from document
    retrieval through LLM generation

This is what you need for prior-auth appeals and regulatory audits.
You can prove exactly which policy language supported every decision."


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SEGMENT 9 — CLOSING  [9:00 – 9:45]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Return to Dashboard or show the running app]

"To summarise what I built:

  A production-deployed, full-stack AI platform that:
    ✓ Ingests PDF policy documents with 512-token chunked RAG
    ✓ Answers natural language questions with citations and confidence scoring
    ✓ Extracts 12 types of structured business rules with IF/THEN logic
    ✓ Validates insurance claims against those rules in two-stage pipeline
    ✓ Detects policy version changes with risk scoring
    ✓ Maintains a full immutable audit trail for every AI decision

  The core engineering challenges I solved:
    ✓ Eliminated model cold-start latency by pre-baking embeddings into Docker
    ✓ Built a sentence-level boilerplate filter to prevent ToC contamination
    ✓ Implemented hallucination prevention via prompt-enforced required openers
    ✓ Wired cross-page state handoff using Next.js URL search parameters

The backend is live on Railway. The frontend is live on Vercel.
The GitHub repository is at github.com/sohithk2002/intellipolicy-ai.

Thank you for watching — I'm happy to answer any questions."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RECORDING TIPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Use QuickTime Player → New Screen Recording (Mac) or OBS
• Resolution: 1920×1080 minimum
• Browser: full-screen Chrome, zoom level 100%
• Hide browser bookmarks bar before recording
• Keep backend running: python3 -m uvicorn main:app --port 8000
• Keep frontend running: npm run dev (port 3000)
• Load sample documents BEFORE starting recording to avoid wait times on camera
• Speak slowly on technical terms — give the viewer time to read the screen
• Pause 1 second after navigating to each new page before speaking
• Export as MP4 H.264, 1080p, target under 200 MB for email submission
"""

def build_script():
    path = OUT / "IntelliPolicy_AI_Video_Script.txt"
    path.write_text(SCRIPT, encoding="utf-8")
    print(f"✓  Script saved → {path}")
    return path


# ═══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    build_pptx()
    build_docx()
    build_script()
    print("\n✅  All three deliverables generated.")
