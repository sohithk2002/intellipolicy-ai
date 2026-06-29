"""LLM service — Anthropic / OpenAI / Gemini with intelligent extractive fallback."""
import os
import re
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")

# Persisted on disk so the key survives backend restarts
_CONFIG_FILE = Path(__file__).resolve().parent.parent.parent / ".api_config.json"

_provider_config: dict = {"provider": None, "api_key": None}
_anthropic_client = None
_openai_client    = None

_STOPWORDS = {
    "what", "which", "where", "when", "how", "does", "are", "the", "and",
    "for", "with", "this", "that", "from", "about", "have", "been", "will",
    "under", "over", "into", "their", "they", "were", "can", "than",
    "also", "such", "more", "some", "any", "not",
}


def _load_persisted_config() -> None:
    """Load API key from disk on startup (survives restarts)."""
    global _provider_config
    try:
        if _CONFIG_FILE.exists():
            data = json.loads(_CONFIG_FILE.read_text())
            if data.get("provider") and data.get("api_key"):
                _provider_config = {"provider": data["provider"], "api_key": data["api_key"]}
                logger.info(f"[LLM] Loaded persisted provider '{data['provider']}' from disk")
    except Exception as e:
        logger.warning(f"[LLM] Could not load persisted config: {e}")


def _save_config() -> None:
    """Write current provider+key to disk."""
    try:
        _CONFIG_FILE.write_text(json.dumps({
            "provider": _provider_config["provider"],
            "api_key":  _provider_config["api_key"],
        }))
    except Exception as e:
        logger.warning(f"[LLM] Could not persist config: {e}")


# Load on import so the key is available immediately after a restart
_load_persisted_config()


def set_api_key(provider: str, api_key: str) -> None:
    global _anthropic_client, _openai_client, _provider_config
    _provider_config = {"provider": provider.lower(), "api_key": api_key}
    _anthropic_client = None
    _openai_client    = None
    _save_config()
    logger.info(f"[LLM] Provider set to '{provider}' and persisted to disk")


def get_active_provider() -> dict:
    return {
        "provider": _provider_config["provider"],
        "has_key":  bool(_provider_config["api_key"] or os.environ.get("ANTHROPIC_API_KEY")),
    }


def _get_anthropic_client():
    global _anthropic_client
    if _anthropic_client is not None:
        return _anthropic_client
    key = _provider_config["api_key"] if _provider_config["provider"] == "anthropic" else None
    key = key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None
    try:
        from anthropic import Anthropic
        _anthropic_client = Anthropic(api_key=key)
        return _anthropic_client
    except Exception as e:
        logger.warning(f"Anthropic client init failed: {e}")
        return None


def _get_openai_client():
    global _openai_client
    if _openai_client is not None:
        return _openai_client
    key = _provider_config["api_key"] if _provider_config["provider"] == "openai" else None
    key = key or os.environ.get("OPENAI_API_KEY")
    if not key:
        return None
    try:
        from openai import OpenAI
        _openai_client = OpenAI(api_key=key)
        return _openai_client
    except Exception as e:
        logger.warning(f"OpenAI client init failed: {e}")
        return None


def _call_llm(prompt: str, max_tokens: int = 1024) -> str | None:
    provider = _provider_config.get("provider")
    if not provider:
        if os.environ.get("ANTHROPIC_API_KEY"):
            provider = "anthropic"
        elif os.environ.get("OPENAI_API_KEY"):
            provider = "openai"

    if provider == "anthropic":
        client = _get_anthropic_client()
        if not client:
            return None
        resp = client.messages.create(
            model=MODEL, max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text

    if provider == "openai":
        client = _get_openai_client()
        if not client:
            return None
        resp = client.chat.completions.create(
            model="gpt-4o-mini", max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content

    if provider == "gemini":
        key = _provider_config["api_key"] or os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not key:
            return None
        try:
            import google.generativeai as genai
            genai.configure(api_key=key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            return model.generate_content(prompt).text
        except Exception as e:
            logger.error(f"Gemini call failed: {e}")
            return None

    return None


# ── Helpers ───────────────────────────────────────────────────────────────────

def _question_keywords(question: str) -> set[str]:
    words = re.split(r"\W+", question.lower())
    return {w for w in words if len(w) > 3 and w not in _STOPWORDS}


def _sentence_overlap_score(sentence: str, keywords: set[str]) -> float:
    if not keywords:
        return 0.0
    sent_words = {w.lower() for w in re.split(r"\W+", sentence) if len(w) > 2}
    return len(keywords & sent_words) / len(keywords)


def _extract_relevant_sentences(text: str, keywords: set[str], max_sentences: int = 3) -> list[str]:
    """Score every sentence in text and return the top ones by keyword overlap."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    scored = [
        (s, _sentence_overlap_score(s, keywords))
        for s in sentences
        if len(s.split()) >= 5
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [s for s, _ in scored[:max_sentences] if scored and scored[0][1] > 0]


def _dynamic_confidence(chunks: list[dict]) -> float:
    """Weighted average of top-3 chunk similarities."""
    weights = [0.55, 0.30, 0.15]
    total = 0.0
    for i, w in enumerate(weights):
        if i < len(chunks):
            total += w * chunks[i].get("relevance_score", 0.0)
    return round(min(total, 1.0), 3)


# ── Helpers for extractive answer formatting ─────────────────────────────────

def _clean_sentence(s: str) -> str:
    """Remove PDF artifacts: lone numbers, header noise, dot-leaders."""
    s = re.sub(r"\.{3,}.*$", "", s)           # dot-leader tails
    s = re.sub(r"^\s*\d{1,3}\s*$", "", s)     # lone page numbers
    s = re.sub(r"\s{2,}", " ", s)
    return s.strip()


_DOC_HEADER_PAT = re.compile(
    r"confidential|for internal use|effective january|effective date.*202\d"
    r"|^\s*page\s+\d+|copyright|\ball rights reserved\b",
    re.IGNORECASE,
)

def _is_toc_sentence(s: str) -> bool:
    """True for ToC entries, PDF headers/footers, and document metadata lines."""
    if re.search(r"\.{3,}\s*\d+\s*$", s):                      # "Section....42"
        return True
    if re.match(r"^\s*\d{1,3}\s*$", s):                          # lone page number
        return True
    if len(s.split()) < 5:                                        # too short
        return True
    if re.match(r"^\d+[\.\d]*\s+[A-Z]", s) and len(s) < 60:    # "12.3 Section Heading"
        return True
    if _DOC_HEADER_PAT.search(s):                                 # document header/footer
        return True
    # Pipe-separated metadata: "Title | Subtitle | Date"
    if s.count("|") >= 1 and len(s) < 120:
        return True
    return False


def _strip_doc_header(text: str) -> str:
    """Remove leading document-header lines (title, date, confidentiality) from chunk text."""
    lines = text.split("\n")
    keep = []
    header_done = False
    for line in lines:
        if not header_done and _DOC_HEADER_PAT.search(line):
            continue   # skip header line
        header_done = True
        keep.append(line)
    return "\n".join(keep)


def _pick_best_sentences(
    context_chunks: list[dict],
    keywords: set[str],
    max_sentences: int = 4,
) -> tuple[list[str], dict]:
    """
    Score every clean sentence in every chunk. Return the top unique sentences
    and the best chunk (for evidence/next_action).
    """
    candidates: list[tuple[float, str, dict]] = []
    for chunk in context_chunks:
        cleaned_text = _strip_doc_header(chunk["text"])
        raw_sents = re.split(r"(?<=[.!?])\s+", cleaned_text)
        for raw in raw_sents:
            sent = _clean_sentence(raw)
            if not sent or _is_toc_sentence(sent) or len(sent.split()) < 7:
                continue
            kw  = _sentence_overlap_score(sent, keywords)
            score = 0.55 * chunk["relevance_score"] + 0.45 * kw
            candidates.append((score, sent, chunk))

    candidates.sort(key=lambda x: x[0], reverse=True)

    seen: set[str] = set()
    top: list[str] = []
    best_chunk = context_chunks[0]

    for score, sent, chunk in candidates:
        norm = re.sub(r"\s+", " ", sent.lower())[:90]
        if norm not in seen:
            seen.add(norm)
            top.append(sent)
            if len(top) == 1:
                best_chunk = chunk   # chunk that gave the highest-scoring sentence
        if len(top) >= max_sentences:
            break

    return top, best_chunk


def _synthesize_answer(sentences: list[str], question: str, best_chunk: dict) -> str:
    """
    Turn the extracted sentences into a readable paragraph rather than
    pasting them verbatim end-to-end.
    """
    if not sentences:
        return "I could not find sufficient information in the uploaded document."

    # Ensure each sentence ends properly and starts capitalised
    cleaned = []
    for s in sentences:
        s = s.strip()
        if s and not s[-1] in ".!?":
            s += "."
        if s:
            s = s[0].upper() + s[1:]
            cleaned.append(s)

    return " ".join(cleaned)


def _make_evidence(best_chunk: dict, keywords: set[str], question: str) -> str:
    """One or two sentences explaining why this page answers the question."""
    page   = best_chunk["page_number"]
    doc    = best_chunk["document_name"]
    sim    = best_chunk["relevance_score"]

    # Extract a short heading/topic from the chunk (first non-trivial line)
    first_lines = [l.strip() for l in best_chunk["text"].split("\n") if len(l.strip()) > 10]
    topic_hint  = first_lines[0][:70] if first_lines else "this topic"

    # Describe the keyword match
    matched = sorted(keywords & {w.lower() for w in re.split(r"\W+", best_chunk["text"]) if len(w) > 3})
    kw_desc = ", ".join(f'"{w}"' for w in matched[:4]) if matched else "the query terms"

    return (
        f"Page {page} of {doc} ({sim:.0%} match) contains language addressing {kw_desc}. "
        f"The section beginning \"{topic_hint}\" directly supports this answer."
    )


def _make_next_action(best_chunk: dict, question: str) -> str:
    """Specific, question-aware recommended action."""
    page  = best_chunk["page_number"]
    doc   = best_chunk["document_name"]

    q_lower = question.lower()

    if any(w in q_lower for w in ["modifier", "billing code", "cpt"]):
        return f"Confirm the modifier usage with your billing team and cross-check with page {page} of {doc} before submitting the claim."
    if any(w in q_lower for w in ["facility", "nonfacility", "non-facility", "setting"]):
        return f"Verify the place-of-service code on the claim and apply the correct rate from page {page} of {doc}."
    if any(w in q_lower for w in ["technician", "interpret", "audiolog", "test result"]):
        return f"Ensure the interpreting provider is a qualified physician or licensed practitioner per page {page} of {doc} before billing the interpretation."
    if any(w in q_lower for w in ["fee schedule", "payment", "rate", "reimburs"]):
        return f"Use the RVU-based calculation described on page {page} of {doc} when pricing this service."
    if any(w in q_lower for w in ["prior auth", "authorization", "pre-cert"]):
        return f"Submit the prior authorization request with documentation listed on page {page} of {doc} before scheduling the procedure."
    if any(w in q_lower for w in ["bundl", "includ", "separately"]):
        return f"Do not bill the bundled services separately. Refer to page {page} of {doc} for the complete list of included components."

    return (
        f"Review page {page} of {doc} and confirm this policy language applies to your "
        "specific claim before proceeding."
    )


# ── Extractive fallback (no API key) ─────────────────────────────────────────

def _extractive_qa(question: str, context_chunks: list[dict]) -> dict:
    if not context_chunks:
        return {
            "answer":              "I could not find sufficient information in the uploaded document.",
            "confidence":          0.0,
            "evidence":            "No relevant chunks retrieved from the vector store.",
            "next_action":         "Upload a policy document first, then re-ask your question.",
            "reasoning_steps":     [],
            "follow_up_questions": [],
        }

    keywords   = _question_keywords(question)
    confidence = _dynamic_confidence(context_chunks)

    # Select the best sentences; get the most informative chunk
    top_sentences, best_chunk = _pick_best_sentences(context_chunks, keywords, max_sentences=4)

    answer     = _synthesize_answer(top_sentences, question, best_chunk)
    evidence   = _make_evidence(best_chunk, keywords, question)
    next_action= _make_next_action(best_chunk, question)

    reasoning_steps = [
        "Embedded query using BAAI/bge-small-en-v1.5 (384-dim)",
        f"Retrieved {len(context_chunks)} chunks; top similarity {context_chunks[0]['relevance_score']:.2f}",
        f"Best chunk: {best_chunk['document_name']} p.{best_chunk['page_number']}",
        f"Scored {sum(1 for c in context_chunks for s in re.split(r'(?<=[.!?])\\s+', c['text']) if len(s.split()) >= 7)} candidate sentences; selected {len(top_sentences)}",
        f"Confidence: {confidence:.2f} (weighted avg of top-3 chunk similarities)",
        "Extractive mode — configure an API key in Dashboard for LLM-quality answers",
    ]

    follow_ups = _generate_extractive_followups(question, context_chunks[:3])

    return {
        "answer":              answer,
        "confidence":          confidence,
        "evidence":            evidence,
        "next_action":         next_action,
        "reasoning_steps":     reasoning_steps,
        "follow_up_questions": follow_ups,
    }


def _generate_extractive_followups(question: str, chunks: list[dict]) -> list[str]:
    """Generate 3 follow-up questions from the retrieved chunk content."""
    # Extract section headings and key phrases from the chunks
    all_text = " ".join(c["text"] for c in chunks)
    headings = re.findall(r"\d+\.\s+([A-Z][^.]{10,60})", all_text)
    cpt_codes = re.findall(r"CPT\s+(?:code\s+)?(\d{5})", all_text, re.IGNORECASE)

    followups: list[str] = []

    if cpt_codes:
        followups.append(f"What are the documentation requirements for CPT {cpt_codes[0]}?")
    if headings:
        followups.append(f"What does the policy say about {headings[0].strip().lower()}?")
    if len(chunks) > 1:
        followups.append(
            f"Are there any exceptions or exclusions related to this policy on page {chunks[1]['page_number']}?"
        )

    # Defaults if not enough material
    defaults = [
        "What services require prior authorization under this policy?",
        "What are the effective dates for this policy?",
        "Are there any documentation requirements for claims?",
    ]
    for d in defaults:
        if len(followups) >= 3:
            break
        if d not in followups:
            followups.append(d)

    return followups[:3]


# ── Extractive rule extraction helpers ───────────────────────────────────────

_MONTHS = {
    "january":"01","february":"02","march":"03","april":"04",
    "may":"05","june":"06","july":"07","august":"08",
    "september":"09","october":"10","november":"11","december":"12",
}

_CPT_PAT  = re.compile(
    r"CPT\s+codes?\s*[:\-]?\s*"           # "CPT code(s):" or "CPT code(s) "
    r"(\d{5}[A-Z]?"                        # first 5-digit code
    r"(?:\s*[,/;]\s*\d{5}[A-Z]?)*)",      # optional additional codes
    re.IGNORECASE,
)
_JCODE_PAT = re.compile(r"\bJ-?codes?\b|J\d{4}", re.IGNORECASE)
_AUTH_PAT  = re.compile(
    r"require[sd]?\s+prior\s+auth(?:orization)?"
    r"|prior\s+auth(?:orization)?\s+(?:is\s+)?required"
    r"|must\s+(?:obtain|submit|get)\s+(?:prior\s+)?auth"
    r"|before\s+(?:prior\s+)?approval"
    r"|require[sd]?\s+step\s+therapy",
    re.IGNORECASE,
)
_PLAN_PAT  = re.compile(
    r"\b(Commercial|Medicare\s+Advantage|Medicaid|All\s+Plans?|All\s+plan\s+types?)\b",
    re.IGNORECASE,
)
_DATE_PAT  = re.compile(
    r"(January|February|March|April|May|June|July|August|September|October|November|December)"
    r"\s+(\d{1,2}),?\s+(\d{4})",
    re.IGNORECASE,
)
_DOC_PAT   = re.compile(
    r"step\s+therapy[^.;\n]{0,60}"
    r"|physician\s+order"
    r"|clinical\s+notes?"
    r"|medical\s+necessity"
    r"|(?:prior\s+auth\w*\s+)?(?:portal|submission|request)[^.;\n]{0,40}"
    r"|certificate\s+of\s+medical\s+necessity"
    r"|documentation\s+required[^.;\n]{0,40}",
    re.IGNORECASE,
)
# Authorization timing: "at least 72 hours prior to the scheduled service"
_TIMING_PAT = re.compile(
    r"(?:at\s+least\s+)?(\d+\s*(?:business\s+)?(?:hours?|days?|weeks?))"
    r"\s+(?:prior\s+to|before|in\s+advance\s+of)"
    r"(?:\s+the)?\s+(?:scheduled\s+)?(?:service|procedure|appointment|visit)",
    re.IGNORECASE,
)
# Emergency window: "within 24 hours post-service / after service"
_EMERGENCY_PAT = re.compile(
    r"within\s+(\d+\s*(?:hours?|days?))"
    r"\s+(?:post[- ]?service|after\s+(?:the\s+)?(?:emergency\s+)?(?:service|visit|encounter|procedure|approval))",
    re.IGNORECASE,
)
# [Page N] markers embedded by extract-rules-from-document endpoint
_PAGE_MARKER = re.compile(r"\[Page\s+(\d+)\]", re.IGNORECASE)


def _parse_effective_date(text: str) -> str | None:
    m = _DATE_PAT.search(text)
    if not m:
        return None
    month = _MONTHS.get(m.group(1).lower(), "01")
    day   = m.group(2).zfill(2)
    year  = m.group(3)
    return f"{year}-{month}-{day}"


def _extract_timing(ctx: str) -> str | None:
    """Return normalised authorization timing, e.g. '72 hours before scheduled service'."""
    m = _TIMING_PAT.search(ctx)
    if not m:
        return None
    qty = m.group(1).strip()
    return f"{qty} before scheduled service"


def _extract_emergency(ctx: str) -> str | None:
    """Return normalised emergency window, e.g. 'within 24 hours after service'."""
    m = _EMERGENCY_PAT.search(ctx)
    if not m:
        return None
    qty = m.group(1).strip()
    return f"within {qty} after service"


def _source_page_from_ctx(text: str, match_start: int) -> int | None:
    """Return the page number from the nearest preceding [Page N] marker, or None."""
    markers = list(_PAGE_MARKER.finditer(text[:match_start]))
    if markers:
        return int(markers[-1].group(1))
    return None


_TRANSITIONAL = re.compile(
    r"^(?:this|that|these|those|it|they|such|the\s+following|as\s+noted|per\s+the)\b",
    re.IGNORECASE,
)

def _extract_procedure_name(before: str, after: str, fallback: str) -> str:
    """
    Best-effort procedure label from text surrounding a CPT mention.
    Constrained to the current sentence only — never bleeds across paragraphs.
    """
    # Only look in the CURRENT sentence (text after the last sentence-ending punctuation)
    current = re.split(r"[.!?]\s+|\n\n", before)[-1].strip()

    # Pattern A: "Procedure Name (CPT codes..." — noun phrase before open paren
    paren_m = re.search(
        r"([A-Za-z][A-Za-z\s\-]+?(?:procedure[s]?|service[s]?|visit[s]?|test[s]?|"
        r"medication[s]?|treatment[s]?|imaging|scan[s]?|therap(?:y|ies)|"
        r"administration|request[s]?)?)\s*\(\s*$",
        current,
    )
    if paren_m:
        return paren_m.group(1).strip()

    # Pattern B: first non-transitional noun phrase in the current sentence
    if current and len(current.split()) > 1 and not _TRANSITIONAL.match(current):
        words  = current.split()[:6]
        phrase = " ".join(words).strip(" ,;:-(")
        if len(phrase) > 4:
            return phrase

    # Pattern C: first medical noun phrase right AFTER the CPT code
    # e.g. "CPT code 99213 office visits require..."
    after_m = re.match(
        r"\s*(\w[\w\s\-]+?(?:visit[s]?|service[s]?|procedure[s]?|"
        r"test[s]?|medication[s]?|administration))",
        after,
    )
    if after_m:
        return after_m.group(1).strip()

    return fallback


def _normalize_plan(raw: str) -> str:
    s = re.sub(r"\s+", " ", raw).strip()
    if re.search(r"medicare\s+advantage", s, re.IGNORECASE):
        return "Medicare Advantage"
    if re.search(r"commercial", s, re.IGNORECASE):
        return "Commercial"
    if re.search(r"medicaid", s, re.IGNORECASE):
        return "Medicaid"
    if re.search(r"all\s+plans?", s, re.IGNORECASE):
        return "All Plans"
    return s.title()


_TIMING_DOC_NOISE = re.compile(r"\d+\s*(?:hours?|days?)\s+(?:prior|before|after|post)", re.IGNORECASE)

def _build_docs(ctx: str, requires_auth: bool) -> list[str]:
    raw = _DOC_PAT.findall(ctx)
    docs = [d.strip().rstrip(",.;") for d in raw if len(d.strip()) > 4]
    # Drop entries that are really timing/emergency text (shown in their own fields)
    docs = list({d for d in docs if not _TIMING_DOC_NOISE.search(d)})[:5]
    if not docs and requires_auth:
        docs = ["Authorization request", "Clinical documentation"]
    return docs


def _rule_confidence(proc_name: str, cpt_str: str, auth: bool,
                     plan_found: bool, date_found: bool, docs: list) -> float:
    score = 0.60
    if proc_name and proc_name != cpt_str:
        score += 0.08
    if auth:
        score += 0.08
    if plan_found:
        score += 0.08
    if date_found:
        score += 0.08
    if docs:
        score += 0.06
    return round(min(score, 0.97), 2)


# ── Rule-type detection (modal verb engine) ───────────────────────────────────

# Ordered: first match wins, so more-specific patterns go first
_RULE_TYPE_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("Provider Restriction", re.compile(
        r"\b(?:technicians?|audiologists?|non-physicians?|unlicensed\s+\w+)"
        r"(?:\s+\w+){0,4}\s+(?:shall|must|may|cannot)\b"
        r"|(?:shall|must|may)\s+not\s+(?:interpret|diagnose|perform|bill\s+for)",
        re.IGNORECASE,
    )),
    ("Prior Authorization", re.compile(
        r"prior\s+auth(?:orization)?|pre-?authoriz|authorization\s+(?:is\s+)?required"
        r"|must\s+(?:obtain|submit|get)\s+(?:prior\s+)?auth",
        re.IGNORECASE,
    )),
    ("Supervision", re.compile(
        r"\bsupervision\b|under\s+(?:direct\s+)?supervision|supervisory\s+requirement"
        r"|direct\s+physician\s+supervision",
        re.IGNORECASE,
    )),
    ("Prohibitions", re.compile(
        r"\b(?:shall\s+not|must\s+not|may\s+not|prohibited|not\s+allowed|not\s+permitted|forbidden)\b",
        re.IGNORECASE,
    )),
    ("Frequency Limits", re.compile(
        r"(?:no\s+more\s+than|limited\s+to|maximum\s+of)\s+\d+"
        r"|\d+\s+times?\s+(?:per|a)\s+(?:year|day|month|quarter|visit)"
        r"|per\s+(?:calendar\s+)?year\b|rolling\s+\d+.?day",
        re.IGNORECASE,
    )),
    ("Time Windows", re.compile(
        r"\d+\s+(?:hours?|days?|weeks?)\s+(?:prior\s+to|before|after|post.?service|within)",
        re.IGNORECASE,
    )),
    ("Documentation", re.compile(
        r"documentation\s+required|medical\s+necessity|clinical\s+notes?"
        r"|must\s+(?:include|submit|provide|attach|contain)\b",
        re.IGNORECASE,
    )),
    ("Billing", re.compile(
        r"bill\s+separately|(?:un)?bundl|modifier\b|report\s+(?:together|with)"
        r"|separately\s+(?:payable|reportable|billable)",
        re.IGNORECASE,
    )),
    ("Payment", re.compile(
        r"payment|reimburs(?:e|ement)?|fee\s+schedule|allowable\s+(?:charge|amount)|rate\b",
        re.IGNORECASE,
    )),
    ("Coverage", re.compile(
        r"(?:is|are|will\s+be)\s+covered|coverage\s+(?:includes?|applies?)"
        r"|benefit\s+(?:includes?|coverage)|(?:not\s+)?covered\s+(?:under|by)",
        re.IGNORECASE,
    )),
    ("Eligibility", re.compile(
        r"eligib(?:le|ility)|qualif(?:y|ied|ication)|must\s+meet\s+criteria"
        r"|coverage\s+criteria|member\s+must\s+be",
        re.IGNORECASE,
    )),
    ("Coding", re.compile(
        r"(?:report|use|append)\s+(?:CPT|ICD|HCPCS|modifier)\b"
        r"|modifier\s+\d{2}|diagnosis\s+code\s+required",
        re.IGNORECASE,
    )),
    ("Exceptions", re.compile(
        r"\bexcept(?:ion)?\s+(?:applies?|granted|when|where|for|in)\b|\bexcept\s+when\b"
        r"|\bunless\b|\bwaiver?\b|\boverride\b",
        re.IGNORECASE,
    )),
]

_MODAL_TRIGGER = re.compile(
    r"\b(?:must(?:\s+not)?|shall(?:\s+not)?|may(?:\s+not)?"
    r"|required?\s+to|required\b|prohibited\b|not\s+allowed|not\s+permitted"
    r"|only\s+(?:when|if)|unless\b|except\s+(?:when|where))\b",
    re.IGNORECASE,
)

_ACTOR_PAT_STRICT = re.compile(
    r"\b(technicians?|physicians?|attending\s+physicians?|treating\s+physicians?"
    r"|ordering\s+physicians?|providers?|specialists?|nurses?|audiologists?"
    r"|therapists?|licensed\s+practitioners?|practitioners?|clinicians?"
    r"|radiologists?|pathologists?|anesthesiologists?|plan\s+members?|members?"
    r"|subscribers?|patients?|facilities|hospitals?|billers?)\b",
    re.IGNORECASE,
)

# Sentences that are headings/administrative noise rather than actionable rules
_NOISE_PAT = re.compile(
    r"^(?:this\s+(?:document|policy|section|manual|guide)|see\s+(?:section|page|also)"
    r"|for\s+(?:more|additional)\s+information|as\s+(?:noted|stated|described)"
    r"|the\s+following\s+(?:rules?|policies?|requirements?))",
    re.IGNORECASE,
)


def _detect_rule_type(sentence: str) -> str:
    for rule_type, pat in _RULE_TYPE_PATTERNS:
        if pat.search(sentence):
            return rule_type
    if _AUTH_PAT.search(sentence):
        return "Prior Authorization"
    return "Policy"


def _extract_actor(sentence: str) -> str | None:
    m = _ACTOR_PAT_STRICT.search(sentence)
    return m.group(1).strip().title() if m else None


def _extract_restriction(sentence: str) -> str | None:
    m = re.search(
        r"(?:shall\s+not|must\s+not|may\s+not|cannot|prohibited\s+(?:from\s+)?"
        r"|not\s+allowed\s+to|not\s+permitted\s+to)\s+([^,;.\n]{5,120})",
        sentence, re.IGNORECASE,
    )
    return m.group(1).strip().rstrip(".,;") if m else None


def _extract_allowed_action(sentence: str) -> str | None:
    # Explicit permission after prohibition: "but may X"
    m = re.search(r"\bbut\s+(?:may|can)\s+(?!not\b)([^.;,\n]{5,120})", sentence, re.IGNORECASE)
    if m:
        return m.group(1).strip().rstrip(".,;")
    # Standalone "may X" where it's not a negation
    m = re.search(
        r"\b(?:may|is\s+allowed\s+to|is\s+permitted\s+to)\s+(?!not\b)([^.;,\n]{5,120})",
        sentence, re.IGNORECASE,
    )
    if m:
        txt = m.group(1).strip()
        if not re.match(r"(?:not|never)\b", txt, re.IGNORECASE):
            return txt.rstrip(".,;")
    return None


def _extract_condition(sentence: str) -> str | None:
    # "under (direct) (physician) supervision"
    m = re.search(r"under\s+((?:\w+\s+){0,4}supervision)", sentence, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    # "only when/if X"
    m = re.search(r"\bonly\s+(?:when|if)\s+([^,;.\n]{5,80})", sentence, re.IGNORECASE)
    if m:
        return m.group(1).strip().rstrip(".,;")
    # "unless X"
    m = re.search(r"\bunless\s+([^,;.\n]{5,80})", sentence, re.IGNORECASE)
    if m:
        return m.group(1).strip().rstrip(".,;")
    # "provided that X" / "in cases where X"
    m = re.search(r"(?:provided\s+that|in\s+cases?\s+(?:where|of))\s+([^,;.\n]{5,80})", sentence, re.IGNORECASE)
    if m:
        return m.group(1).strip().rstrip(".,;")
    return None


# ── CPT/J-code rule extraction (existing logic, preserved exactly) ────────────

def _extractive_rules_cpt(text: str, eff_date: str | None) -> list[dict]:
    rules: list[dict] = []
    seen_cpt: set[str] = set()

    for m in _CPT_PAT.finditer(text):
        raw_codes = m.group(1)
        codes     = re.findall(r"\d{5}[A-Z]?", raw_codes)
        cpt_str   = ", ".join(codes)
        if cpt_str in seen_cpt:
            continue
        seen_cpt.add(cpt_str)

        ctx_start = max(0, m.start() - 400)
        ctx_end   = min(len(text), m.end() + 500)
        ctx       = text[ctx_start:ctx_end]
        before    = text[ctx_start:m.start()]
        after     = text[m.end():ctx_end]

        para_s = text.rfind("\n\n", 0, m.start())
        para_s = (para_s + 2) if para_s != -1 else ctx_start
        para_e = text.find("\n\n", m.end())
        para_e = para_e if para_e != -1 else ctx_end
        para_ctx = text[para_s:para_e]

        proc_name     = _extract_procedure_name(before, after, cpt_str)
        requires_auth = bool(_AUTH_PAT.search(para_ctx))
        plan_m        = _PLAN_PAT.search(para_ctx)
        plan_type     = _normalize_plan(plan_m.group(1) if plan_m else "All Plans")
        docs          = _build_docs(para_ctx, requires_auth)
        timing        = _extract_timing(para_ctx)
        emergency     = _extract_emergency(para_ctx)
        conf          = _rule_confidence(proc_name, cpt_str, requires_auth,
                                         bool(plan_m), bool(eff_date), docs)
        suffix        = "Prior Authorization" if requires_auth else "Billing Rule"
        rule_type     = "Prior Authorization" if requires_auth else "Billing"

        rules.append({
            "procedure":                    f"{proc_name} — {suffix}",
            "cpt_code":                     cpt_str,
            "plan_type":                    plan_type,
            "requires_prior_authorization": requires_auth,
            "documentation_required":       docs,
            "effective_date":               eff_date,
            "authorization_timing":         timing,
            "emergency_exception":          emergency,
            "source_page":                  _source_page_from_ctx(text, m.start()),
            "confidence":                   conf,
            "raw_text":                     ctx[:300],
            "rule_type":                    rule_type,
            "actor":                        None,
            "restriction":                  None,
            "allowed_action":               None,
            "condition":                    None,
        })

    for m in _JCODE_PAT.finditer(text):
        ctx_start  = max(0, m.start() - 400)
        ctx_end    = min(len(text), m.end() + 500)
        ctx        = text[ctx_start:ctx_end]
        para_s_j   = text.rfind("\n\n", 0, m.start())
        para_s_j   = (para_s_j + 2) if para_s_j != -1 else ctx_start
        para_e_j   = text.find("\n\n", m.end())
        para_e_j   = para_e_j if para_e_j != -1 else ctx_end
        para_ctx_j = text[para_s_j:para_e_j]

        if not _AUTH_PAT.search(para_ctx_j):
            continue

        before    = text[ctx_start:m.start()]
        after     = text[m.end():ctx_end]
        proc_name = _extract_procedure_name(before, after, "Specialty Drug")
        plan_m    = _PLAN_PAT.search(para_ctx_j)
        plan_type = _normalize_plan(plan_m.group(1) if plan_m else "All Plans")
        docs      = _build_docs(para_ctx_j, True)
        timing_j  = _extract_timing(para_ctx_j)
        emerg_j   = _extract_emergency(para_ctx_j)
        conf      = _rule_confidence(proc_name, "J-codes", True,
                                      bool(plan_m), bool(eff_date), docs)

        rules.append({
            "procedure":                    f"{proc_name} — Prior Authorization",
            "cpt_code":                     "J-codes",
            "plan_type":                    plan_type,
            "requires_prior_authorization": True,
            "documentation_required":       docs,
            "effective_date":               eff_date,
            "authorization_timing":         timing_j,
            "emergency_exception":          emerg_j,
            "source_page":                  _source_page_from_ctx(text, m.start()),
            "confidence":                   conf,
            "raw_text":                     ctx[:300],
            "rule_type":                    "Prior Authorization",
            "actor":                        None,
            "restriction":                  None,
            "allowed_action":               None,
            "condition":                    None,
        })

    return rules


# ── Modal-verb sentence-level rule extraction ─────────────────────────────────

def _extractive_rules_modal(text: str, eff_date: str | None, seen: set[str]) -> list[dict]:
    """
    Scans every sentence for deontic modal verbs (must/shall/may/prohibited/…)
    and converts actionable policy statements into structured rules.
    Covers: Provider Restrictions, Supervision, Prohibitions, Coverage, Documentation,
    Billing, Payment, Coding, Frequency Limits, Time Windows, Eligibility, Exceptions.
    """
    rules: list[dict] = []
    sentences = re.split(r"(?<=[.!?])\s+|\n{2,}", text)

    for sent in sentences:
        sent = sent.strip()
        if len(sent.split()) < 6:
            continue
        if _NOISE_PAT.match(sent):
            continue
        if not _MODAL_TRIGGER.search(sent):
            continue

        key = re.sub(r"\s+", " ", sent[:70].lower())
        if key in seen:
            continue
        seen.add(key)

        rule_type    = _detect_rule_type(sent)
        actor        = _extract_actor(sent)
        restriction  = _extract_restriction(sent)
        allowed      = _extract_allowed_action(sent)
        condition    = _extract_condition(sent)

        plan_m = _PLAN_PAT.search(sent)
        if not plan_m:
            plan_m = _PLAN_PAT.search(text[:600])
        plan_type = _normalize_plan(plan_m.group(1) if plan_m else "All Plans")

        requires_auth = bool(_AUTH_PAT.search(sent)) or rule_type == "Prior Authorization"
        docs = _build_docs(sent, requires_auth)

        # Quality gate: skip purely generic sentences with no useful signal
        has_signal = (
            actor is not None
            or restriction is not None
            or allowed is not None
            or condition is not None
            or rule_type not in ("Policy",)
        )
        if not has_signal:
            continue

        # Confidence
        conf = 0.65
        if actor:                       conf += 0.07
        if restriction or allowed:      conf += 0.08
        if condition:                   conf += 0.06
        if plan_m:                      conf += 0.05
        if eff_date:                    conf += 0.03
        conf = round(min(conf, 0.92), 2)

        # Procedure label
        if actor:
            proc = f"{actor} — {rule_type}"
        else:
            words = sent.split()[:5]
            proc = " ".join(words).rstrip(".,;:") + f" — {rule_type}"

        sent_pos = text.find(sent[:40]) if len(sent) >= 40 else text.find(sent)
        source_page = _source_page_from_ctx(text, sent_pos) if sent_pos >= 0 else None

        rules.append({
            "procedure":                    proc,
            "cpt_code":                     None,
            "plan_type":                    plan_type,
            "requires_prior_authorization": requires_auth,
            "documentation_required":       docs,
            "effective_date":               eff_date,
            "authorization_timing":         _extract_timing(sent),
            "emergency_exception":          _extract_emergency(sent),
            "source_page":                  source_page,
            "confidence":                   conf,
            "raw_text":                     sent[:300],
            "rule_type":                    rule_type,
            "actor":                        actor,
            "restriction":                  restriction,
            "allowed_action":               allowed,
            "condition":                    condition,
        })

    return rules


# ── Extractive fallbacks for rules + validation ───────────────────────────────

def _extractive_rules(text: str) -> list[dict]:
    """
    Full rule extraction combining CPT/J-code and modal-verb engines.
    Handles Prior Authorization, Payment, Billing, Coverage, Documentation,
    Provider Restrictions, Supervision, Coding, Frequency Limits, Time Windows,
    Eligibility, Exceptions, and Prohibitions — with or without CPT codes.
    """
    eff_date = _parse_effective_date(text)

    # Pass 1 — CPT / J-code anchored rules
    cpt_rules = _extractive_rules_cpt(text, eff_date)

    # Seed seen-set so modal engine doesn't duplicate CPT sentence text
    seen: set[str] = set()
    for r in cpt_rules:
        seen.add(re.sub(r"\s+", " ", r["raw_text"][:70].lower()))

    # Pass 2 — Modal-verb sentence scan (all other rule types)
    modal_rules = _extractive_rules_modal(text, eff_date, seen)

    return cpt_rules + modal_rules


def _extractive_validate(claim: dict, rules: list[dict]) -> dict:
    if not rules:
        return {
            "decision": "Needs Review",
            "reason": "No policy rules extracted. Please extract rules from a policy document first.",
            "missing_info": ["Extracted policy rules"],
            "policy_source": "No policy document available",
            "source_page": None,
            "confidence": 0.0,
            "rule_matched": False,
            "next_steps": ["Upload a policy document", "Extract rules", "Re-validate claim"],
        }

    cpt = claim.get("cpt_code", "").strip()
    proc = claim.get("procedure", "").lower()

    for rule in rules:
        rule_cpt = rule.get("cpt_code", "") or ""
        if cpt and rule_cpt:
            parts = re.split(r"[,/\s]+", rule_cpt)
            if any(cpt == part.strip() for part in parts if part.strip()):
                page_ref = f"page {rule['source_page']}" if rule.get("source_page") else "Manual input"
                if rule.get("requires_prior_authorization"):
                    return {
                        "decision": "Needs Review",
                        "reason": f"CPT {cpt} requires prior authorization per {rule.get('procedure', 'extracted rule')}.",
                        "missing_info": rule.get("documentation_required", []),
                        "policy_source": f"Extracted rules ({page_ref})",
                        "source_page": rule.get("source_page"),
                        "confidence": rule.get("confidence", 0.7),
                        "rule_matched": True,
                        "document_fallback_performed": False,
                        "next_steps": ["Obtain prior authorization", "Submit required documentation"],
                    }
                return {
                    "decision": "Approved",
                    "reason": f"CPT {cpt} does not require prior authorization per {rule.get('procedure', 'extracted rule')}.",
                    "missing_info": [],
                    "policy_source": f"Extracted rules ({page_ref})",
                    "source_page": rule.get("source_page"),
                    "confidence": rule.get("confidence", 0.7),
                    "rule_matched": True,
                    "document_fallback_performed": False,
                    "next_steps": ["Submit claim for processing"],
                }

    # Actor / restriction keyword match for non-CPT rules
    for rule in rules:
        actor = (rule.get("actor") or "").lower()
        restriction = (rule.get("restriction") or "").lower()
        raw = (rule.get("raw_text") or "").lower()

        matched = False
        if actor:
            actor_words = [w for w in re.split(r"\W+", actor) if len(w) > 3]
            if actor_words and any(w in proc for w in actor_words):
                matched = True
        if not matched and restriction:
            restr_words = [w for w in re.split(r"\W+", restriction) if len(w) > 4]
            if restr_words and sum(1 for w in restr_words if w in proc) >= 2:
                matched = True
        if not matched and cpt and len(cpt) == 5 and cpt in raw:
            matched = True

        if matched:
            page_ref = f"page {rule['source_page']}" if rule.get("source_page") else "extracted rules"
            rule_type = rule.get("rule_type", "Policy Restriction")
            actor_str = rule.get("actor", "")
            restriction_str = rule.get("restriction", "")
            if restriction_str:
                reason = f"{actor_str}: {restriction_str}." if actor_str else restriction_str
            else:
                reason = rule.get("raw_text", "")[:200] or f"Policy rule matched: {rule_type}"
            decision = "Denied" if rule_type in ("Provider Restriction", "Prohibitions") else "Needs Review"
            return {
                "decision": decision,
                "reason": reason,
                "missing_info": rule.get("documentation_required", []),
                "policy_source": f"Extracted rules ({page_ref})",
                "source_page": rule.get("source_page"),
                "confidence": rule.get("confidence", 0.75),
                "rule_matched": True,
                "document_fallback_performed": False,
                "next_steps": [
                    f"Review the {rule_type} policy for this procedure",
                    "Ensure the claim meets all documented requirements",
                ],
            }

    return {
        "decision": "Needs Review",
        "reason": f"CPT {cpt or 'code'} was not found in extracted rules.",
        "missing_info": [],
        "policy_source": "Extracted policy rules",
        "source_page": None,
        "confidence": 0.3,
        "rule_matched": False,
        "document_fallback_performed": False,
        "next_steps": ["Verify CPT code is covered", "Extract rules from a relevant policy document"],
    }


def check_rule_match(claim: dict, rules: list[dict]) -> dict | None:
    """
    Deterministically return the first rule that matches the claim, or None.
    Matching is purely keyword/CPT — no LLM involved.
    """
    if not rules:
        return None

    cpt = claim.get("cpt_code", "").strip()
    proc = claim.get("procedure", "").lower()

    for rule in rules:
        rule_cpt = rule.get("cpt_code", "") or ""
        if cpt and rule_cpt:
            parts = re.split(r"[,/\s]+", rule_cpt)
            if any(cpt == part.strip() for part in parts if part.strip()):
                return rule

    for rule in rules:
        actor = (rule.get("actor") or "").lower()
        restriction = (rule.get("restriction") or "").lower()
        raw = (rule.get("raw_text") or "").lower()

        if actor:
            actor_words = [w for w in re.split(r"\W+", actor) if len(w) > 3]
            if actor_words and any(w in proc for w in actor_words):
                return rule
        if restriction:
            restr_words = [w for w in re.split(r"\W+", restriction) if len(w) > 4]
            if restr_words and sum(1 for w in restr_words if w in proc) >= 2:
                return rule
        if cpt and len(cpt) == 5 and cpt in raw:
            return rule

    return None


# ── Public API ────────────────────────────────────────────────────────────────

def ask_with_context(
    question: str,
    context_chunks: list[dict],
    conversation_history: list[dict] | None = None,
) -> dict:
    """Generate an answer grounded strictly in context_chunks."""

    # Build conversation context string for the prompt
    history_text = ""
    if conversation_history:
        history_text = "\n\nPREVIOUS CONVERSATION:\n"
        for turn in conversation_history[-3:]:  # last 3 turns
            history_text += f"User: {turn['question']}\nAssistant: {turn['answer']}\n"

    context_text = "\n\n---\n\n".join([
        f"[Document: {c['document_name']} | Page {c['page_number']} | Similarity: {c['relevance_score']:.2f}]\n{c['text']}"
        for c in context_chunks
    ])

    prompt = f"""You are a strict healthcare policy analyst. Your ONLY source of truth is the POLICY CONTEXT below.
You must NEVER use outside knowledge, training data, or assumptions. Every statement must be directly supported by the provided text.

{history_text}

POLICY CONTEXT:
{context_text}

QUESTION: {question}

GROUNDING RULES — ALL are mandatory:

1. Read every chunk carefully. Determine if the POLICY CONTEXT explicitly answers the question.

2. STRONG SIGNAL REQUIRED — only answer "found" if the context contains at least one of:
   - The exact CPT/HCPCS code mentioned in the question
   - The exact procedure or service name
   - The exact policy term (prior authorization, coverage, billing, etc.)
   - A sentence that directly answers the question

3. If the context clearly answers the question:
   - Set "not_found": false
   - "answer": Plain English, 2-4 sentences. No raw policy text. No section numbers.
   - "confidence": 0.50–1.0 based on how completely the context answers the question
   - "evidence": 1-2 sentences explaining SPECIFICALLY which page/section supports the answer and why
   - "next_action": One concrete instruction referencing the exact page number

4. If the context does NOT clearly answer the question (weak match, unrelated content, or general policy text that does not address the specific question):
   - Set "not_found": true
   - Set "answer" to EXACTLY this phrase: "This is not mentioned in the uploaded document."
   - Set "confidence" below 0.50
   - "follow_up_questions": 3 questions the document DOES answer well

5. NEVER guess, infer, or use background knowledge. If unsure → not_found: true.

6. "reasoning_steps": List the actual retrieval facts (chunk count, top similarity, pages). Do NOT invent steps.

Respond with ONLY valid JSON — no markdown, no explanation outside the JSON:
{{
  "not_found": false,
  "answer": "Concise plain-English answer directly from the document",
  "confidence": 0.87,
  "evidence": "Specific explanation of why page N of DocumentName supports this answer",
  "next_action": "Specific analyst instruction referencing the exact page number and topic",
  "follow_up_questions": [
    "Specific question this document answers well",
    "Specific question this document answers well",
    "Specific question this document answers well"
  ],
  "reasoning_steps": [
    "Retrieved N chunks from vector store",
    "Top similarity: X.XX — DocumentName p.N",
    "Pages used: N, N",
    "Answer grounded in context"
  ]
}}"""

    raw = _call_llm(prompt, max_tokens=1200)
    if raw is None:
        logger.warning("[LLM] No API key — using extractive fallback")
        return _extractive_qa(question, context_chunks)

    try:
        start = raw.find("{")
        end   = raw.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(raw[start:end])
        return json.loads(raw)
    except Exception as e:
        logger.error(f"[LLM] JSON parse failed: {e}")
        return _extractive_qa(question, context_chunks)


def extract_rules_from_text(text: str) -> list[dict]:
    prompt = f"""Extract every business rule from this healthcare policy text. Do NOT limit to prior-authorization rules.

SUPPORTED RULE TYPES (detect all that apply):
Prior Authorization, Payment, Billing, Coverage, Documentation, Provider Restriction,
Supervision, Coding, Frequency Limits, Time Windows, Eligibility, Exceptions, Prohibitions

KEY RULE TRIGGERS — treat sentences containing these as rules:
must, must not, shall, shall not, may, may not, required, prohibited, only, except, unless

POLICY TEXT:
{text}

Return a JSON array. Every rule needs ALL of these fields:
[{{
  "procedure":                    "Short label, e.g. Technician — Provider Restriction",
  "rule_type":                    "One of the 13 types above",
  "actor":                        "Who the rule applies to, or null",
  "restriction":                  "What is restricted/prohibited, or null",
  "allowed_action":               "What is explicitly allowed (for mixed rules), or null",
  "condition":                    "Under what condition the rule applies, or null",
  "cpt_code":                     "NNNNN or null",
  "plan_type":                    "Commercial|Medicare Advantage|All Plans|etc.",
  "requires_prior_authorization": true,
  "documentation_required":       ["item1"],
  "effective_date":               "YYYY-MM-DD or null",
  "source_page":                  1,
  "confidence":                   0.9,
  "raw_text":                     "exact sentence that generated this rule"
}}]

IMPORTANT:
- A rule does NOT need a CPT code.
- Provider restriction rules (technician/audiologist/non-physician) ARE valid rules.
- If absolutely no actionable policy statement exists, return: []"""

    try:
        raw = _call_llm(prompt, max_tokens=2048)
        if raw is None:
            return _extractive_rules(text)
        start = raw.find("[")
        end   = raw.rfind("]") + 1
        if start >= 0 and end > start:
            return json.loads(raw[start:end])
        return []
    except Exception as e:
        logger.error(f"[LLM] extract_rules_from_text failed: {e}")
        return _extractive_rules(text)


def _extractive_compare(old_text: str, new_text: str) -> dict:
    """
    Keyword-driven extractive comparison used when no LLM is configured.
    Finds sentences mentioning key policy signals and diffs them between versions.
    """
    _POLICY_SIGNALS = re.compile(
        r"prior\s+auth|require[sd]?|effective\s+date|CPT\s+\d{5}|step\s+therapy"
        r"|coverage|authorization|telehealth|documentation|parity|formulary"
        r"|emergency|bundl|modifier|place\s+of\s+service|medical\s+necessity"
        r"|deductible|copay|coinsurance|out.of.pocket|network|referral",
        re.IGNORECASE,
    )

    def _policy_sentences(text: str) -> list[str]:
        sents = re.split(r"(?<=[.!?])\s+|\n{2,}", text)
        return [s.strip() for s in sents if len(s.split()) >= 8 and _POLICY_SIGNALS.search(s)]

    def _norm(s: str) -> str:
        return re.sub(r"\s+", " ", s.lower().strip())

    old_sents = _policy_sentences(old_text)
    new_sents = _policy_sentences(new_text)

    old_norms = {_norm(s): s for s in old_sents}
    new_norms = {_norm(s): s for s in new_sents}

    changes: list[dict] = []

    # Sentences in new but not in old → something was added/changed
    added = [s for n, s in new_norms.items() if n not in old_norms]
    # Sentences in old but not in new → something was removed/changed
    removed = [s for n, s in old_norms.items() if n not in new_norms]

    # Pair them up as best-effort "before/after" by keyword overlap
    def _overlap(a: str, b: str) -> float:
        wa = set(re.split(r"\W+", a.lower()))
        wb = set(re.split(r"\W+", b.lower()))
        shared = wa & wb - {"the", "a", "an", "is", "are", "of", "to", "in", "and", "or", "for"}
        return len(shared) / max(len(wa | wb), 1)

    used_removed: set[int] = set()
    for new_s in added[:10]:
        best_idx, best_score = -1, 0.0
        for i, old_s in enumerate(removed):
            if i in used_removed:
                continue
            sc = _overlap(old_s, new_s)
            if sc > best_score:
                best_score, best_idx = sc, i

        if best_idx >= 0 and best_score >= 0.25:
            old_s = removed[best_idx]
            used_removed.add(best_idx)
            # Infer change type
            ctype = "Authorization"
            if re.search(r"CPT|billing|modifier|bundl", new_s, re.IGNORECASE):
                ctype = "Billing"
            elif re.search(r"effective|date|period", new_s, re.IGNORECASE):
                ctype = "Administrative"
            elif re.search(r"coverage|telehealth|benefit", new_s, re.IGNORECASE):
                ctype = "Coverage"
            # Infer risk
            risk = "medium"
            if re.search(r"prior\s+auth|require[sd]?|step\s+therapy|denied?|emergency", new_s, re.IGNORECASE):
                risk = "high"
            elif re.search(r"effective|date|administrative", new_s, re.IGNORECASE):
                risk = "low"
            # Short label from first 6 words of the new sentence
            words = new_s.split()
            area = " ".join(words[:6]).rstrip(".,;:") if words else "Policy Language"
            changes.append({
                "area":        area,
                "old_value":   old_s[:200],
                "new_value":   new_s[:200],
                "impact":      "Policy language changed — review for operational impact",
                "risk_level":  risk,
                "change_type": ctype,
            })
        else:
            # Purely new sentence with no match
            words = new_s.split()
            area = " ".join(words[:6]).rstrip(".,;:") if words else "New Requirement"
            ctype = "Authorization" if re.search(r"auth|require", new_s, re.IGNORECASE) else "Coverage"
            changes.append({
                "area":        area,
                "old_value":   "Not present in previous version",
                "new_value":   new_s[:200],
                "impact":      "New policy requirement identified",
                "risk_level":  "medium",
                "change_type": ctype,
            })
        if len(changes) >= 8:
            break

    high = sum(1 for c in changes if c["risk_level"] == "high")
    summary = (
        f"Extractive comparison identified {len(changes)} policy language changes "
        f"({high} high-risk). Configure an API key in Dashboard for a more detailed AI analysis."
        if changes else
        "The two documents appear structurally similar — no distinct policy language differences detected. "
        "Configure an API key in Dashboard for a deeper AI-powered comparison."
    )
    return {"summary": summary, "changes": changes}


def compare_policy_sections(old_text: str, new_text: str) -> dict:
    prompt = f"""Compare OLD and NEW healthcare policy text. Identify all meaningful changes.

OLD POLICY:
{old_text[:3000]}

NEW POLICY:
{new_text[:3000]}

Return JSON:
{{
  "summary": "Executive summary of most important changes",
  "changes": [{{
    "area": "Change area",
    "old_value": "Old policy language",
    "new_value": "New policy language",
    "impact": "Business impact for claims/analysts",
    "risk_level": "high|medium|low",
    "change_type": "Authorization|Billing|Coverage|Administrative|Documentation"
  }}]
}}"""

    try:
        raw = _call_llm(prompt, max_tokens=2048)
        if raw is None:
            return _extractive_compare(old_text, new_text)
        start = raw.find("{")
        end   = raw.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(raw[start:end])
        return {"summary": "Comparison complete", "changes": []}
    except Exception as e:
        logger.error(f"[LLM] compare_policy_sections failed: {e}")
        return _extractive_compare(old_text, new_text)


def validate_claim_against_rules(claim: dict, rules: list[dict]) -> dict:
    rules_text = json.dumps(rules, indent=2)
    prompt = f"""Validate this healthcare claim against the extracted policy rules.

CLAIM:
CPT Code: {claim.get('cpt_code', '')}
Diagnosis: {claim.get('diagnosis_code', '')}
Plan Type: {claim.get('plan_type', '')}
Procedure: {claim.get('procedure', '')}
Service Date: {claim.get('service_date', '')}

POLICY RULES:
{rules_text[:3000]}

If POLICY RULES is empty, return decision "Needs Review" explaining no rules are loaded.

Return JSON:
{{
  "decision": "Approved|Denied|Needs Review",
  "reason": "Clear explanation citing the specific rule",
  "missing_info": ["list of missing items"],
  "policy_source": "Document and section reference",
  "source_page": 18,
  "confidence": 0.94,
  "rule_matched": true,
  "next_steps": ["Step 1", "Step 2"]
}}"""

    try:
        raw = _call_llm(prompt, max_tokens=1024)
        if raw is None:
            return _extractive_validate(claim, rules)
        start = raw.find("{")
        end   = raw.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(raw[start:end])
        return _extractive_validate(claim, rules)
    except Exception as e:
        logger.error(f"[LLM] validate_claim_against_rules failed: {e}")
        return _extractive_validate(claim, rules)
