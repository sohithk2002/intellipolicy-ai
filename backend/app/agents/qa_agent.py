"""Policy QA Agent — retrieve → re-rank → generate → audit."""
import uuid
import re
import logging
from datetime import datetime
from .retrieval_agent import run_retrieval
from ..services.llm_service import ask_with_context
from ..services.vector_store import RetrievedChunk, get_global_store

logger = logging.getLogger(__name__)

_audit_store:   dict[str, dict] = {}
_session_history: dict[str, list[dict]] = {}   # session_id -> [{question, answer}]

MIN_RELEVANCE   = 0.08   # below this → truly unrelated content
MIN_CONFIDENCE  = 0.20   # post-LLM: only reject if very low AND explicit not_found flag
MIN_SIGNAL_SCORE = 0.15  # after reranking, top chunk must meet this OR keyword overlap ≥ 20%

STOPWORDS = {
    "what", "which", "where", "when", "how", "does", "are", "the", "and",
    "for", "with", "this", "that", "from", "about", "have", "been", "will",
    "under", "over", "into", "their", "they", "were", "can", "than", "also",
}

_CASUAL_RE = re.compile(
    r"^(?:hi+|hello|hey|how are you|how.?s it going|what.?s up|"
    r"good\s+(?:morning|afternoon|evening|day)|thanks?(?:\s+you)?|"
    r"bye|goodbye|who are you|what (?:are|can) you|are you there|test(?:ing)?)\b",
    re.IGNORECASE,
)

_NOT_FOUND_PHRASES = {
    "could not find", "not mentioned", "not in the", "not found",
    "no information", "not addressed", "does not appear", "not covered in",
    "not present", "unable to find", "this is not mentioned",
}


def _is_casual(question: str) -> bool:
    return bool(_CASUAL_RE.match(question.strip()))


def _casual_response(question: str, session_id: str) -> dict:
    q = question.lower()
    if any(g in q for g in ["how are you", "how's", "how is"]):
        answer = "I'm doing well and ready to help you analyze healthcare policy documents. Ask me anything about your uploaded policy."
    elif any(g in q for g in ["who are you", "what are you"]):
        answer = "I'm IntelliPolicy AI — a healthcare policy assistant. I can answer questions about uploaded policy documents, validate claims, and extract structured rules. Upload a policy document to get started."
    elif any(g in q for g in ["what can you", "can you help"]):
        answer = "I can answer questions about uploaded healthcare policy documents, help validate CPT claims against policy rules, and extract structured business rules from policy text."
    else:
        answer = "Hello! I'm here to help with healthcare policy questions. Upload a policy document and ask me anything about coverage, prior authorization, billing codes, and more."
    return {
        "answer":             answer,
        "confidence":         1.0,
        "citations":          [],
        "evidence":           "",
        "next_action":        "Upload a policy document and ask a policy-specific question to get started.",
        "session_id":         session_id,
        "reasoning_steps":    ["Conversational question — no document retrieval needed"],
        "follow_up_questions": [
            "What services require prior authorization under this policy?",
            "What documentation is required for claims?",
            "What procedures are covered under this policy?",
        ],
    }


def _has_strong_signal(question: str, chunks: list[RetrievedChunk]) -> bool:
    """
    True if at least one retrieved chunk has a relevant signal to the question.
    Uses permissive thresholds — the LLM itself makes the final grounding decision.
    """
    # General summary/overview questions always pass — let the LLM answer from top chunks
    _GENERAL_PATTERNS = re.compile(
        r"^(what (is|are|does)|summarize|overview|explain|describe|tell me|"
        r"what can you|give me|list|show me|how does|why does)",
        re.IGNORECASE,
    )
    if _GENERAL_PATTERNS.match(question.strip()):
        return True

    q_codes = re.findall(r"\b\d{5}[A-Z]?\b|\b[A-Z]\d{4}\b", question)
    q_words = {w.lower() for w in re.split(r"\W+", question)
               if len(w) > 3 and w.lower() not in STOPWORDS}

    for chunk in chunks:
        text_lower = chunk.text.lower()
        # Exact CPT/HCPCS code
        if q_codes and any(code.lower() in text_lower for code in q_codes):
            return True
        # Keyword overlap ≥ 20% (with at least 1 hit)
        if q_words:
            hits = sum(1 for w in q_words if w in text_lower)
            if hits >= max(1, len(q_words) * 0.20):
                return True
        # Meets minimum reranked score
        if chunk.relevance_score >= MIN_SIGNAL_SCORE:
            return True
    return False


def _search_keywords_desc(question: str) -> str:
    """Human-readable description of what was searched for."""
    q_codes = re.findall(r"\b\d{5}[A-Z]?\b|\b[A-Z]\d{4}\b", question)
    q_words = [w for w in re.split(r"\W+", question)
               if len(w) > 3 and w.lower() not in STOPWORDS]
    parts = []
    if q_codes:
        parts.append(f"CPT/HCPCS code(s) {', '.join(q_codes)}")
    if q_words:
        parts.append(f"keywords: {', '.join(q_words[:6])}")
    return ", ".join(parts) if parts else f'"{question[:60]}"'


def _suggest_from_chunks(chunks: list[RetrievedChunk], current_question: str = "") -> list[str]:
    """Generate 3 contextually relevant follow-up questions, never repeating the current one."""
    defaults = [
        "What documentation must be submitted with a claim?",
        "What CPT codes are mentioned in this document?",
        "Which procedures are excluded or require special review?",
        "What are the billing rules for telehealth services?",
        "What are the evaluation and management (E/M) coding guidelines?",
    ]
    if not chunks:
        return [d for d in defaults if d.lower() not in current_question.lower()][:3]

    all_text = " ".join(c.text for c in chunks[:3])
    cpt_codes = re.findall(r"CPT\s*(?:code\s+)?(\d{5})", all_text, re.IGNORECASE)
    headings  = re.findall(r"(?:^|\n)([A-Z][A-Za-z ]{5,50})(?:\n|:)", all_text)

    q_lower = current_question.lower()
    suggestions: list[str] = []
    if cpt_codes:
        candidate = f"What are the documentation requirements for CPT {cpt_codes[0]}?"
        if candidate.lower() not in q_lower:
            suggestions.append(candidate)
    if headings:
        h = headings[0].strip().lower()
        candidate = f"What does the policy say about {h}?"
        if h not in q_lower and candidate.lower() not in q_lower:
            suggestions.append(candidate)
    for d in defaults:
        if len(suggestions) >= 3:
            break
        if d.lower() not in q_lower:
            suggestions.append(d)
    return suggestions[:3]


def _is_llm_not_found(llm_result: dict) -> bool:
    """True only when the LLM explicitly signals it could not find the answer."""
    if llm_result.get("not_found") is True:
        conf   = llm_result.get("confidence", 1.0)
        answer = (llm_result.get("answer") or "").lower()
        # Only reject if BOTH the flag is set AND the answer contains a not-found phrase
        if any(p in answer for p in _NOT_FOUND_PHRASES):
            return True
        # Or if confidence is extremely low
        if conf < MIN_CONFIDENCE:
            return True
    return False


def _keyword_overlap(question: str, text: str) -> float:
    """Fraction of question keywords found in the chunk text."""
    q_words = {w.lower() for w in re.split(r"\W+", question) if len(w) > 3 and w.lower() not in STOPWORDS}
    if not q_words:
        return 0.0
    t_words = {w.lower() for w in re.split(r"\W+", text)}
    return len(q_words & t_words) / len(q_words)


def _is_toc_chunk(text: str) -> bool:
    """
    Detect table-of-contents / index chunks so they are excluded from answer context.
    ToC chunks are characterised by many short lines and line-ending page numbers.
    """
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if len(lines) < 4:
        return False
    total      = len(lines)
    short      = sum(1 for l in lines if len(l) < 60)
    # line ends with digits (page ref) or has dot-leaders
    page_ref   = sum(1 for l in lines if re.search(r"\.{2,}\s*\d+\s*$|\s{2,}\d{1,3}\s*$", l))
    full_sents = sum(1 for l in lines if l.endswith(".") and len(l) > 50)
    return (short / total > 0.65) and (page_ref / total > 0.30) and (full_sents / total < 0.15)


def _rerank(chunks: list[RetrievedChunk], question: str, top_k: int = 5) -> list[RetrievedChunk]:
    """
    Combined score = 0.70 * cosine_similarity + 0.30 * keyword_overlap.
    Surfaces chunks that are both semantically and lexically relevant.
    """
    scored = []
    for c in chunks:
        kw  = _keyword_overlap(question, c.text)
        combined = 0.70 * c.relevance_score + 0.30 * kw
        scored.append((combined, c))

    scored.sort(key=lambda x: x[0], reverse=True)
    # Rebuild relevance_score with the combined value for downstream confidence
    reranked = []
    for combined_score, c in scored[:top_k]:
        reranked.append(RetrievedChunk(
            document_id    = c.document_id,
            document_name  = c.document_name,
            page_number    = c.page_number,
            text           = c.text,
            relevance_score= round(combined_score, 4),
        ))
    return reranked


_OVERVIEW_RE = re.compile(
    r"^(?:what\s+is\s+this|what\s+does\s+this\s+document|summarize|give\s+(?:me\s+)?(?:an?\s+)?overview|"
    r"overview\s+of|describe\s+this|tell\s+me\s+about\s+this|what\s+is\s+in\s+this|"
    r"what\s+(?:topics?|subjects?|sections?)\s+(?:are\s+)?(?:covered|discussed|included)|"
    r"what\s+can\s+i\s+(?:ask|find)|what\s+(?:information|content)\s+is\s+(?:in|available))",
    re.IGNORECASE,
)


def _is_overview_question(question: str) -> bool:
    return bool(_OVERVIEW_RE.match(question.strip()))


def _overview_response(
    question: str,
    session_id: str,
    document_ids: list[str] | None,
) -> dict | None:
    """
    For "what is this document about?" style questions, build an answer from
    the first few pages of the document (intro/scope sections) rather than
    doing a keyword search that returns random policy clauses.
    Returns None if no document chunks found (fall through to normal pipeline).
    """
    store = get_global_store()
    all_chunks = store.get_all_chunks()
    if document_ids:
        doc_chunks = [c for c in all_chunks if c["document_id"] in document_ids]
    else:
        doc_chunks = all_chunks

    if not doc_chunks:
        return None

    # Sort by page number; skip Table-of-Contents pages, take first 6 real-content chunks
    doc_chunks_sorted = sorted(doc_chunks, key=lambda c: c.get("page_number", 0))
    non_toc = [c for c in doc_chunks_sorted if not _is_toc_chunk(c.get("text", ""))]
    first_chunks = (non_toc[:6] if len(non_toc) >= 3 else doc_chunks_sorted[:6])

    doc_name = first_chunks[0]["document_name"].replace(".pdf", "")

    # Build a clean summary from the first chunks
    lines: list[str] = []
    seen: set[str] = set()
    for chunk in first_chunks:
        for sent in re.split(r"(?<=[.!?])\s+", chunk["text"]):
            sent = sent.strip()
            if len(sent.split()) < 8:
                continue
            norm = re.sub(r"\s+", " ", sent.lower())[:80]
            if norm in seen:
                continue
            # Skip page numbers, headers, dot leaders
            if re.search(r"\.{3,}|\bpage\s+\d+\b|^\d+\s*$", sent):
                continue
            seen.add(norm)
            lines.append(sent)
            if len(lines) >= 5:
                break
        if len(lines) >= 5:
            break

    context_chunks = [
        {
            "document_id":     c["document_id"],
            "document_name":   c["document_name"],
            "page_number":     c["page_number"],
            "text":            c["text"],
            "relevance_score": 0.85,
        }
        for c in first_chunks
    ]

    # Try the LLM first with these intro-page chunks
    try:
        llm_result = ask_with_context(question, context_chunks)
    except Exception as e:
        logger.warning(f"[QAAgent] Overview LLM call failed: {e}")
        llm_result = None

    if llm_result and not _is_llm_not_found(llm_result):
        answer = llm_result.get("answer", "")
        confidence = llm_result.get("confidence", 0.75)
        reasoning = [
            "Detected overview/summary question",
            f"Fetched first {len(first_chunks)} page(s) of {doc_name}",
            "Passed introduction sections to LLM for synthesis",
        ] + (llm_result.get("reasoning_steps") or [])
        follow_ups = llm_result.get("follow_up_questions") or [
            "What services require prior authorization?",
            "What CPT codes are covered under this policy?",
            "What documentation is required for claims?",
        ]
        evidence = llm_result.get("evidence") or f"Answer synthesized from pages 1–{first_chunks[-1]['page_number']} of {doc_name}."
        next_action = llm_result.get("next_action") or "Ask specific questions about coverage, prior authorization, billing codes, or any topic in the document."
    else:
        # Extractive fallback
        if not lines:
            return None
        body = " ".join(lines[:5])
        answer = f"**{doc_name}** is a healthcare policy document covering:\n\n{body}"
        confidence = 0.65
        reasoning = [
            "Detected overview/summary question",
            f"Fetched first {len(first_chunks)} page(s) — extractive mode (no API key)",
        ]
        follow_ups = [
            "What services require prior authorization?",
            "What CPT codes are covered under this policy?",
            "What documentation is required for claims?",
        ]
        evidence = f"Answer built from pages 1–{first_chunks[-1]['page_number']} of {doc_name} (introduction/scope sections)."
        next_action = "Configure an API key in the Dashboard for a richer AI-generated summary."

    citations = [
        {
            "document_id":     c["document_id"],
            "document_name":   c["document_name"],
            "page_number":     c["page_number"],
            "text":            c["text"][:280] + ("…" if len(c["text"]) > 280 else ""),
            "relevance_score": 0.85,
        }
        for c in first_chunks[:3]
    ]

    ts = datetime.utcnow().isoformat()
    _audit_store[session_id] = {
        "session_id":        session_id,
        "question":          question,
        "retrieved_pages":   sorted({c["page_number"] for c in first_chunks}),
        "reasoning_summary": "\n".join(reasoning),
        "final_answer":      answer,
        "confidence":        confidence,
        "source_citations":  citations,
        "steps":             [{"step": s, "description": s, "timestamp": ts} for s in reasoning],
        "created_at":        ts,
    }

    return {
        "answer":             answer,
        "confidence":         confidence,
        "citations":          citations,
        "evidence":           evidence,
        "next_action":        next_action,
        "session_id":         session_id,
        "reasoning_steps":    reasoning,
        "follow_up_questions": follow_ups,
    }


def run_qa(
    question:     str,
    document_ids: list[str] | None = None,
    session_id:   str | None = None,
) -> dict:
    session_id = session_id or str(uuid.uuid4())
    logger.info(f"[QAAgent] Session {session_id}: {question[:80]}")

    # ── Step 0: Casual / conversational question — skip RAG entirely ─────────
    if _is_casual(question):
        logger.info("[QAAgent] Casual question — skipping retrieval")
        return _casual_response(question, session_id)

    # Overview/summary questions go through the normal pipeline with a larger top_k
    # so the LLM gets a representative cross-section of the document.

    # ── Step 1: Retrieve (more chunks for overview questions) ────────────────
    is_overview = _is_overview_question(question)
    try:
        raw_chunks = run_retrieval(question, top_k=20 if is_overview else 15, document_ids=document_ids)
    except Exception as e:
        logger.error(f"[QAAgent] Retrieval failed: {e}")
        raw_chunks = []

    if not raw_chunks:
        return _not_found_response(question, session_id, reason="no_documents")

    # ── Step 2: Relevance threshold (very permissive — LLM does final check) ─
    top_score = raw_chunks[0].relevance_score
    if top_score < MIN_RELEVANCE:
        return _not_found_response(
            question, session_id, reason="low_relevance",
            top_score=top_score, search_desc=_search_keywords_desc(question),
        )

    # ── Step 3: Re-rank ───────────────────────────────────────────────────────
    chunks = _rerank(raw_chunks, question, top_k=10 if is_overview else 7)

    # ── Step 3b: Remove ToC chunks when substantive content is available ──────
    non_toc = [c for c in chunks if not _is_toc_chunk(c.text)]
    if len(non_toc) >= 2:
        chunks = non_toc

    # ── Step 3c: Strong-signal validation ────────────────────────────────────
    if not _has_strong_signal(question, chunks):
        logger.info("[QAAgent] No strong signal in retrieved chunks — not found")
        return _not_found_response(
            question, session_id, reason="weak_signal",
            search_desc=_search_keywords_desc(question), chunks=chunks,
        )

    # ── Step 4: Assemble context dicts ────────────────────────────────────────
    context = [
        {
            "document_id":    c.document_id,
            "document_name":  c.document_name,
            "page_number":    c.page_number,
            "text":           c.text,
            "relevance_score":c.relevance_score,
        }
        for c in chunks
    ]

    # ── Step 5: Build real pipeline trace BEFORE calling LLM ─────────────────
    pages_used = sorted({c.page_number for c in chunks})
    docs_used  = sorted({c.document_name for c in chunks})
    pipeline_steps = [
        f"Embedded query using BAAI/bge-small-en-v1.5 (384-dim)",
        f"Retrieved {len(raw_chunks)} candidates from vector store",
        f"Re-ranked by combined score (70% semantic + 30% keyword)",
        f"Top chunk: {chunks[0].document_name} p.{chunks[0].page_number} "
        f"(similarity {chunks[0].relevance_score:.2f})",
        f"Pages used: {', '.join(str(p) for p in pages_used)}",
        f"Documents: {', '.join(docs_used)}",
    ]

    # ── Step 6: Load conversation history for this session ───────────────────
    history = _session_history.get(session_id, [])

    # ── Step 7: LLM answer generation ────────────────────────────────────────
    try:
        llm_result = ask_with_context(question, context, conversation_history=history)
    except Exception as e:
        logger.error(f"[QAAgent] LLM call failed: {e}")
        llm_result = {
            "answer":      "Unable to generate answer. Please try again.",
            "confidence":  0.0,
            "evidence":    "",
            "next_action": "Retry the question.",
            "reasoning_steps":    [],
            "follow_up_questions":[],
        }

    # ── Step 7b: Post-LLM grounding check ────────────────────────────────────
    if _is_llm_not_found(llm_result):
        logger.info(f"[QAAgent] LLM signalled not-found (conf={llm_result.get('confidence',0):.2f})")
        return _not_found_response(
            question, session_id, reason="llm_not_found",
            search_desc=_search_keywords_desc(question),
            chunks=chunks,
            suggested_questions=llm_result.get("follow_up_questions") or [],
        )

    # Use LLM reasoning steps if provided, otherwise use our real pipeline trace
    final_reasoning = llm_result.get("reasoning_steps") or pipeline_steps
    # Always prepend the real retrieval steps so the trace is never purely fabricated
    if llm_result.get("reasoning_steps"):
        final_reasoning = pipeline_steps[:3] + llm_result["reasoning_steps"]

    pipeline_steps.append(
        f"Answer generated with confidence {llm_result.get('confidence', 0.0):.0%}"
    )

    # ── Step 8: Build citations (snippet, not full chunk) ─────────────────────
    citations = []
    for c in chunks[:3]:
        # Use first 280 chars as the citation snippet — not the full chunk
        snippet = c.text[:280].strip()
        if len(c.text) > 280:
            snippet += "…"
        citations.append({
            "document_id":    c.document_id,
            "document_name":  c.document_name,
            "page_number":    c.page_number,
            "text":           snippet,
            "relevance_score":c.relevance_score,
        })

    # ── Step 9: Update conversation history ───────────────────────────────────
    answer_text = llm_result.get("answer", "")
    _session_history.setdefault(session_id, []).append({
        "question": question,
        "answer":   answer_text[:400],  # keep truncated for prompt budget
    })

    # ── Step 10: Audit record ─────────────────────────────────────────────────
    response = {
        "answer":             answer_text,
        "confidence":         llm_result.get("confidence", 0.0),
        "citations":          citations,
        "evidence":           llm_result.get("evidence", ""),
        "next_action":        llm_result.get("next_action", ""),
        "session_id":         session_id,
        "reasoning_steps":    final_reasoning,
        "follow_up_questions":llm_result.get("follow_up_questions", []),
    }

    _audit_store[session_id] = {
        "session_id":       session_id,
        "question":         question,
        "retrieved_pages":  pages_used,
        "reasoning_summary":"\n".join(final_reasoning),
        "final_answer":     answer_text,
        "confidence":       response["confidence"],
        "source_citations": citations,
        "steps": [
            {"step": s, "description": s, "timestamp": datetime.utcnow().isoformat()}
            for s in final_reasoning
        ],
        "created_at": datetime.utcnow().isoformat(),
    }

    return response


def get_audit_store() -> dict[str, dict]:
    return _audit_store


def _not_found_response(
    question:           str,
    session_id:         str,
    reason:             str = "no_documents",
    top_score:          float = 0.0,
    search_desc:        str = "",
    chunks:             list | None = None,
    suggested_questions:list | None = None,
) -> dict:
    chunks = chunks or []
    search_label = search_desc or f'"{question[:60]}"'

    if reason == "no_documents":
        answer = "This is not mentioned in the uploaded document."
        why    = "No documents have been uploaded yet. Please upload a policy document first, then re-ask your question."
        reasoning = [
            "Embedded query using BAAI/bge-small-en-v1.5",
            "No documents found in vector store",
            "Answer not generated — no documents uploaded",
        ]
    elif reason == "low_relevance":
        answer = "This is not mentioned in the uploaded document."
        why    = (
            f"I searched for {search_label}, but the retrieved text did not contain "
            f"policy language that answers this question. "
            f"(Best match: {top_score:.0%} similarity — below the {MIN_RELEVANCE:.0%} minimum threshold.)"
        )
        reasoning = [
            "Embedded query using BAAI/bge-small-en-v1.5",
            f"Top chunk similarity {top_score:.2f} — below threshold {MIN_RELEVANCE}",
            "Answer not generated — relevance too low",
        ]
    elif reason == "weak_signal":
        answer = "This is not mentioned in the uploaded document."
        why    = (
            f"I searched for {search_label}, but the retrieved text did not contain "
            f"policy language that answers this question. None of the retrieved sections "
            f"contained a strong match for the specific terms in your question."
        )
        reasoning = [
            "Embedded query using BAAI/bge-small-en-v1.5",
            f"Retrieved {len(chunks)} chunks — none passed strong-signal validation",
            "Answer not generated — no exact CPT code, policy term, or keyword match found",
        ]
    else:  # llm_not_found
        answer = "This is not mentioned in the uploaded document."
        why    = (
            f"I searched for {search_label}, but the retrieved text did not contain "
            f"policy language that clearly answers this question."
        )
        reasoning = [
            "Embedded query using BAAI/bge-small-en-v1.5",
            f"Retrieved {len(chunks)} chunks and sent to LLM",
            "LLM returned low confidence — answer not grounded in document",
        ]

    suggestions = suggested_questions or _suggest_from_chunks(chunks, question)

    ts = datetime.utcnow().isoformat()
    _audit_store[session_id] = {
        "session_id":       session_id,
        "question":         question,
        "retrieved_pages":  [],
        "reasoning_summary":"\n".join(reasoning),
        "final_answer":     answer,
        "confidence":       0.0,
        "source_citations": [],
        "steps":            [{"step": s, "description": s, "timestamp": ts} for s in reasoning],
        "created_at":       ts,
    }

    return {
        "answer":             answer,
        "confidence":         0.0,
        "citations":          [],           # no citations for not-found
        "evidence":           why,
        "next_action":        "Try one of the suggested questions below, or upload a more relevant policy document.",
        "session_id":         session_id,
        "reasoning_steps":    reasoning,
        "follow_up_questions":suggestions,
    }
