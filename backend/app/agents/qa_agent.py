"""Policy QA Agent — retrieve → re-rank → generate → audit."""
import uuid
import re
import logging
from datetime import datetime
from .retrieval_agent import run_retrieval
from ..services.llm_service import ask_with_context
from ..services.vector_store import RetrievedChunk

logger = logging.getLogger(__name__)

_audit_store:   dict[str, dict] = {}
_session_history: dict[str, list[dict]] = {}   # session_id -> [{question, answer}]

MIN_RELEVANCE = 0.15   # below this threshold → "not found"
STOPWORDS = {
    "what", "which", "where", "when", "how", "does", "are", "the", "and",
    "for", "with", "this", "that", "from", "about", "have", "been", "will",
    "under", "over", "into", "their", "they", "were", "can", "than", "also",
}


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


def run_qa(
    question:     str,
    document_ids: list[str] | None = None,
    session_id:   str | None = None,
) -> dict:
    session_id = session_id or str(uuid.uuid4())
    logger.info(f"[QAAgent] Session {session_id}: {question[:80]}")

    ts = datetime.utcnow().isoformat()

    # ── Step 1: Retrieve (top 10 so re-ranker has material) ──────────────────
    try:
        raw_chunks = run_retrieval(question, top_k=10, document_ids=document_ids)
    except Exception as e:
        logger.error(f"[QAAgent] Retrieval failed: {e}")
        raw_chunks = []

    if not raw_chunks:
        return _not_found_response(question, session_id, reason="no_documents")

    # ── Step 2: Relevance threshold ───────────────────────────────────────────
    top_score = raw_chunks[0].relevance_score
    if top_score < MIN_RELEVANCE:
        return _not_found_response(question, session_id, reason="low_relevance", top_score=top_score)

    # ── Step 3: Re-rank ───────────────────────────────────────────────────────
    chunks = _rerank(raw_chunks, question, top_k=5)

    # ── Step 3b: Remove ToC chunks when substantive content is available ──────
    non_toc = [c for c in chunks if not _is_toc_chunk(c.text)]
    if len(non_toc) >= 2:      # keep ToC only when it's all we have
        chunks = non_toc

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
    question:  str,
    session_id:str,
    reason:    str = "no_documents",
    top_score: float = 0.0,
) -> dict:
    if reason == "no_documents":
        answer = "I could not find sufficient information in the uploaded document. No documents have been indexed yet."
        detail = "No chunks found in the vector store. Upload a policy document first."
    else:
        answer = "I could not find sufficient information in the uploaded document."
        detail = (
            f"Best retrieval similarity was {top_score:.2f}, which is below the minimum "
            f"threshold of {MIN_RELEVANCE:.2f}. The document may not contain information about this topic."
        )

    reasoning = [
        "Embedded query using BAAI/bge-small-en-v1.5",
        detail,
        "No answer generated — relevance threshold not met",
    ]

    record = {
        "session_id":         session_id,
        "question":           question,
        "retrieved_pages":    [],
        "reasoning_summary":  "\n".join(reasoning),
        "final_answer":       answer,
        "confidence":         0.0,
        "source_citations":   [],
        "steps":              [{"step": s, "description": s, "timestamp": datetime.utcnow().isoformat()} for s in reasoning],
        "created_at":         datetime.utcnow().isoformat(),
    }
    _audit_store[session_id] = record

    return {
        "answer":             answer,
        "confidence":         0.0,
        "citations":          [],
        "evidence":           detail,
        "next_action":        "Upload the relevant policy document and re-ask your question.",
        "session_id":         session_id,
        "reasoning_steps":    reasoning,
        "follow_up_questions":[],
    }
