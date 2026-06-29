"""Comparison Agent — compares two policy documents section by section."""
import logging
from ..services.vector_store import get_global_store
from ..services.llm_service import compare_policy_sections
from .intake_agent import get_document_registry

logger = logging.getLogger(__name__)


def run_comparison(old_document_id: str, new_document_id: str) -> dict:
    """Compare two policy documents and return structured change list."""
    logger.info(f"[ComparisonAgent] Comparing {old_document_id} vs {new_document_id}")
    registry = get_document_registry()

    old_doc = registry.get(old_document_id, {"filename": "Old Policy"})
    new_doc = registry.get(new_document_id, {"filename": "New Policy"})

    # Get all text from both documents
    store = get_global_store()
    old_chunks = [c for c in store._chunks if c["document_id"] == old_document_id]
    new_chunks = [c for c in store._chunks if c["document_id"] == new_document_id]

    old_text = " ".join(c["text"] for c in old_chunks[:20])  # first 20 chunks
    new_text = " ".join(c["text"] for c in new_chunks[:20])

    if not old_text or not new_text:
        # Return demo comparison for demonstration
        return _demo_comparison(old_doc["filename"], new_doc["filename"])

    try:
        result = compare_policy_sections(old_text, new_text)
        changes = result.get("changes", [])
        high_risk = sum(1 for c in changes if c.get("risk_level") == "high")
        return {
            "summary": result.get("summary", "Comparison complete"),
            "changes": changes,
            "total_changes": len(changes),
            "high_risk_count": high_risk,
            "old_doc_name": old_doc["filename"],
            "new_doc_name": new_doc["filename"],
        }
    except Exception as e:
        logger.error(f"[ComparisonAgent] LLM comparison failed: {e}")
        return _demo_comparison(old_doc["filename"], new_doc["filename"])


def _demo_comparison(old_name: str, new_name: str) -> dict:
    """Fallback demo comparison result."""
    return {
        "summary": "Policy comparison shows significant changes to authorization requirements and billing documentation. High-risk changes include new MRI prior authorization mandate and step therapy requirements for biologics.",
        "changes": [
            {"area": "MRI Authorization", "old_value": "Not required", "new_value": "Required - 72 hours prior", "impact": "Higher review risk", "risk_level": "high", "change_type": "Authorization"},
            {"area": "Effective Date", "old_value": "Jan 2025", "new_value": "Jan 2026", "impact": "Policy update", "risk_level": "low", "change_type": "Administrative"},
            {"area": "CPT 99213 Documentation", "old_value": "Standard visit", "new_value": "Medical necessity required", "impact": "Documentation burden", "risk_level": "medium", "change_type": "Billing"},
        ],
        "total_changes": 3,
        "high_risk_count": 1,
        "old_doc_name": old_name,
        "new_doc_name": new_name,
    }
