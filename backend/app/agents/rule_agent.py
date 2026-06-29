"""Rule Agent — extracts business rules from policy text and validates claims."""
import re
import uuid
import logging
from datetime import datetime
from ..services.llm_service import extract_rules_from_text, validate_claim_against_rules, check_rule_match

logger = logging.getLogger(__name__)

_rules_store: list[dict] = []
_claim_audit_store: dict[str, dict] = {}

# ── Retrieval constants ───────────────────────────────────────────────────────

_POLICY_KW: set[str] = {
    "authorization", "prior auth", "coverage", "payable", "denied", "denial",
    "documentation", "medical necessity", "covered", "benefit", "benefits",
    "network", "deductible", "copay", "approved", "billing", "claim",
    "not covered", "requires", "required", "eligible", "eligibility",
    "restriction", "prohibited", "allowed", "criteria", "guideline",
}

# Words in a procedure description that do NOT identify the medical service
_PROC_STOPWORDS: set[str] = {
    "with", "and", "the", "for", "per", "via", "from", "into", "upon",
    "level", "type", "test", "results", "that", "this", "which", "have",
    "been", "will", "also", "only", "prior", "authorization", "service",
    "services", "visit", "care", "health", "medical", "procedure",
    "treatment", "patient", "provider", "plan", "required", "requires",
}

# Words that strongly indicate a chunk is about unrelated administrative topics
_UNRELATED_KW: set[str] = {
    "graduate medical education", "gme funding", "teaching hospital",
    "residency program", "fellowship program", "medical school",
}

# Rerank score thresholds
_MIN_COSINE = 0.15        # reject at vector-search stage below this
_MIN_RERANK_SCORE = 55.0  # reject after reranking below this
_FETCH_TOP_K = 8          # fetch more chunks so reranker has material


# ── Retrieval helpers ─────────────────────────────────────────────────────────

def _extract_proc_keywords(procedure: str) -> list[str]:
    """Extract meaningful medical/service words from a procedure description."""
    words = re.findall(r"[a-zA-Z]{3,}", procedure)
    return [w for w in words if w.lower() not in _PROC_STOPWORDS]


def _build_query(cpt: str, proc_keywords: list[str], plan_type: str) -> str:
    """Build a focused search query biased toward policy content."""
    parts = []
    if cpt:
        parts.append(cpt)
    if proc_keywords:
        parts.extend(proc_keywords[:6])   # cap to avoid dilution
    if plan_type:
        parts.append(plan_type)
    # Always append policy anchor terms so embeddings skew toward policy chunks
    parts.append("coverage authorization medical necessity documentation")
    return " ".join(parts)


def _passes_guardrail(chunk, cpt: str, proc_keywords: list[str]) -> bool:
    """
    Reject chunks that contain none of: CPT code, procedure keyword, policy keyword.
    Prevents GME/administrative chunks from reaching the validator.
    """
    text = chunk.text.lower()

    if cpt and cpt in text:
        return True

    for kw in proc_keywords:
        if len(kw) >= 3 and kw.lower() in text:
            return True

    for kw in _POLICY_KW:
        if kw in text:
            return True

    return False


def _rerank_score(chunk, cpt: str, proc_keywords: list[str], plan_type: str) -> float:
    """
    Combined relevance score:
      base     = cosine_similarity * 100
      +50      CPT exact match in text
      +30 each procedure keyword match (capped at 3)
      +20      any policy keyword match
      +10      plan type match
      -50      unrelated administrative topic
    """
    text = chunk.text.lower()
    score: float = chunk.relevance_score * 100

    if cpt and cpt in text:
        score += 50

    proc_hits = sum(1 for kw in proc_keywords if kw.lower() in text)
    score += min(proc_hits * 30, 90)   # max +90 from procedure keywords

    if any(kw in text for kw in _POLICY_KW):
        score += 20

    if plan_type and plan_type.lower() in text:
        score += 10

    if any(kw in text for kw in _UNRELATED_KW):
        score -= 50

    return score


# ── Document fallback ─────────────────────────────────────────────────────────

def _document_fallback(claim: dict, document_id: str | None) -> dict:
    """
    Search the vector store for relevant policy text when no structured rule matched.
    Pipeline: build query → vector search → guardrail filter → rerank → threshold.
    """
    from ..services.embeddings import embed_query
    from ..services.vector_store import get_global_store

    cpt       = claim.get("cpt_code", "")
    procedure = claim.get("procedure", "")
    plan_type = claim.get("plan_type", "")

    proc_keywords = _extract_proc_keywords(procedure)
    query = _build_query(cpt, proc_keywords, plan_type)
    logger.info(
        f"[RuleAgent] Fallback query: {query!r} | keywords={proc_keywords} | doc_id={document_id}"
    )

    # ── Vector search ────────────────────────────────────────────────────────
    try:
        embedding = embed_query(query)
        store     = get_global_store()
        doc_filter = [document_id] if document_id else None
        raw_results = store.search(embedding, top_k=_FETCH_TOP_K, document_ids=doc_filter)
    except Exception as e:
        logger.error(f"[RuleAgent] Vector search failed: {e}")
        raw_results = []

    # ── Cosine threshold ─────────────────────────────────────────────────────
    candidates = [r for r in raw_results if r.relevance_score >= _MIN_COSINE]

    # ── Guardrail filter ─────────────────────────────────────────────────────
    candidates = [r for r in candidates if _passes_guardrail(r, cpt, proc_keywords)]

    # ── Rerank ───────────────────────────────────────────────────────────────
    scored = [
        (_rerank_score(r, cpt, proc_keywords, plan_type), r)
        for r in candidates
    ]
    scored.sort(key=lambda x: x[0], reverse=True)
    logger.info(
        f"[RuleAgent] Reranked {len(scored)} candidates: "
        + str([(round(s, 1), c.document_name[:30], c.page_number) for s, c in scored[:3]])
    )

    # ── Apply minimum rerank threshold ────────────────────────────────────────
    strong = [(s, c) for s, c in scored if s >= _MIN_RERANK_SCORE]

    if strong:
        top_score, top = strong[0]
        snippet = top.text[:320].strip()
        if len(top.text) > 320:
            snippet += "…"
        label = f"CPT {cpt}" if cpt else procedure
        confidence = round(min(top_score / 200.0, 0.92), 2)

        reason_lines = [
            f"No structured rule matched {label}.",
            f"Policy evidence retrieved from {top.document_name} (page {top.page_number}):",
            f'"{snippet}"',
        ]
        if len(strong) > 1:
            _, second = strong[1]
            reason_lines.append(
                f"Additional evidence on page {second.page_number} of {second.document_name}."
            )

        return {
            "decision": "Needs Review",
            "reason": "\n\n".join(reason_lines),
            "missing_info": [
                f"Explicit coverage determination for {label} under {plan_type}",
                "Extracted policy rules for automated matching",
            ],
            "policy_source": f"{top.document_name}, page {top.page_number}",
            "source_page": top.page_number,
            "confidence": confidence,
            "rule_matched": False,
            "document_fallback_performed": True,
            "next_steps": [
                f"Review page {top.page_number} of {top.document_name} for {label} coverage determination",
                f"Confirm '{procedure}' meets medical necessity criteria under {plan_type}",
                "Extract business rules from this document to enable automated rule matching on future claims",
            ],
        }

    # ── No relevant evidence found ────────────────────────────────────────────
    label = f"CPT {cpt}" if cpt else procedure
    return {
        "decision": "Needs Review",
        "reason": (
            f"No relevant policy evidence found for this claim ({label}). "
            "The retrieved document chunks did not contain relevant coverage, authorization, or restriction information. "
            f"Upload a policy document that covers {label} under {plan_type} and extract rules before validating."
        ),
        "missing_info": [
            f"Policy document covering {label} under {plan_type}",
            "Extracted business rules for automated matching",
        ],
        "policy_source": "No matching policy document available",
        "source_page": None,
        "confidence": 0.05,
        "rule_matched": False,
        "document_fallback_performed": True,
        "next_steps": [
            f"Upload a policy document that covers {label} under {plan_type}",
            "Extract business rules from the uploaded document",
            "Re-validate the claim after rule extraction completes",
        ],
    }


# ── Core functions ────────────────────────────────────────────────────────────

def run_rule_extraction(text: str, document_id: str | None = None) -> dict:
    """Extract structured business rules from policy text."""
    logger.info(f"[RuleAgent] Extracting rules from {len(text)} chars")
    try:
        rules = extract_rules_from_text(text)
        for rule in rules:
            if "confidence" not in rule:
                rule["confidence"] = 0.85
            if "raw_text" not in rule:
                rule["raw_text"] = text[:200]
        _rules_store.extend(rules)
        logger.info(f"[RuleAgent] Extracted {len(rules)} rules")
        return {"rules": rules, "document_id": document_id, "total_rules": len(rules)}
    except Exception as e:
        logger.error(f"[RuleAgent] Extraction failed: {e}")
        return {"rules": [], "document_id": document_id, "total_rules": 0}


def run_claim_validation(claim: dict) -> dict:
    """
    Validate a claim:
      1. Deterministic structured rule match (no LLM hallucination risk)
      2. If no rule: targeted document fallback with guardrails + reranking
    """
    logger.info(f"[RuleAgent] Validating claim CPT={claim.get('cpt_code')} plan={claim.get('plan_type')}")
    rules       = list(_rules_store[:50])
    document_id = claim.get("document_id")

    # ── Step 1: Structured rule search (deterministic) ────────────────────────
    matched_rule = check_rule_match(claim, rules)

    if matched_rule:
        logger.info(f"[RuleAgent] Rule matched: {matched_rule.get('rule_type', matched_rule.get('procedure'))}")
        try:
            result = validate_claim_against_rules(claim, [matched_rule])
        except Exception as e:
            logger.error(f"[RuleAgent] Post-match validation failed: {e}")
            page_ref    = f"page {matched_rule['source_page']}" if matched_rule.get("source_page") else "extracted rules"
            rule_type   = matched_rule.get("rule_type", "Policy Rule")
            actor       = matched_rule.get("actor", "")
            restriction = matched_rule.get("restriction", "")
            reason      = (
                f"{actor}: {restriction}."
                if (actor and restriction)
                else matched_rule.get("raw_text", rule_type)[:200]
            )
            result = {
                "decision": "Denied" if rule_type in ("Provider Restriction", "Prohibitions") else "Needs Review",
                "reason": reason,
                "missing_info": matched_rule.get("documentation_required", []),
                "policy_source": f"Extracted rules ({page_ref})",
                "source_page": matched_rule.get("source_page"),
                "confidence": matched_rule.get("confidence", 0.7),
                "next_steps": [f"Review {rule_type} policy for this procedure"],
            }
        result["rule_matched"] = True
        result.setdefault("document_fallback_performed", False)

    else:
        # ── Step 2: Targeted document fallback ────────────────────────────────
        logger.info(f"[RuleAgent] No rule matched — running document fallback (doc_id={document_id})")
        result = _document_fallback(claim, document_id)

    # ── Audit record ──────────────────────────────────────────────────────────
    audit_id = str(uuid.uuid4())
    _claim_audit_store[audit_id] = {
        "audit_id":      audit_id,
        "cpt_code":      claim.get("cpt_code", ""),
        "diagnosis_code":claim.get("diagnosis_code", ""),
        "plan_type":     claim.get("plan_type", ""),
        "procedure":     claim.get("procedure", ""),
        "service_date":  claim.get("service_date", ""),
        "decision":      result.get("decision", ""),
        "confidence":    result.get("confidence", 0.0),
        "rule_matched":  bool(result.get("rule_matched", False)),
        "created_at":    datetime.utcnow().isoformat(),
    }

    return result


def get_rules_store() -> list[dict]:
    return _rules_store


def get_claim_audit_store() -> dict[str, dict]:
    return _claim_audit_store
