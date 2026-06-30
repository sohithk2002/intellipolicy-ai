"""FastAPI route handlers for all IntelliPolicy endpoints."""
import os
import uuid
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
from ..models.schemas import (
    AskRequest, AskResponse, CompareRequest, CompareResponse,
    ExtractRulesRequest, ExtractRulesFromDocumentRequest, ExtractRulesResponse,
    ClaimValidationRequest, ClaimValidationResponse,
    DocumentResponse, AuditRecord, DashboardStats,
    Citation, BusinessRule, PolicyChange, AuditStep, ClaimAuditRecord,
)
from ..agents.intake_agent import run_intake, get_document_registry
from ..agents.qa_agent import run_qa, get_audit_store
from ..agents.comparison_agent import run_comparison
from ..agents.rule_agent import (
    run_rule_extraction, run_claim_validation,
    get_rules_store, get_claim_audit_store,
)
from ..services.vector_store import get_document_chunks
from ..services.llm_service import set_api_key, get_active_provider

SAMPLE_DOCS_DIR = Path(__file__).resolve().parent.parent.parent / "sample_docs"

_SAMPLE_LABELS = {
    "prior_authorization_policy_2026.pdf": "Prior Authorization Policy Manual 2026",
    "telehealth_coverage_policy.pdf":      "Telehealth and Virtual Care Coverage Policy 2026",
    "claims_billing_guidelines.pdf":       "Claims Billing and Coding Guidelines 2026",
    "emergency_services_policy.pdf":       "Emergency Services and Urgent Care Coverage Policy 2026",
    "specialty_drug_formulary.pdf":        "Specialty Drug and Formulary Coverage Policy 2026",
    "medical_necessity_guidelines.pdf":    "Medical Necessity and Coverage Determination Guidelines 2026",
}


class ApiKeyRequest(BaseModel):
    provider: str
    api_key: str


class LoadSampleRequest(BaseModel):
    filename: str

router = APIRouter()


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form("policy"),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    if file.size and file.size > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be under 50MB")

    file_bytes = await file.read()
    result = run_intake(file_bytes, file.filename, document_type)
    if result.get("status") == "error":
        raise HTTPException(status_code=422, detail=result.get("error", "Processing failed"))
    return DocumentResponse(**result)


@router.get("/documents", response_model=list[DocumentResponse])
async def list_documents():
    registry = get_document_registry()
    docs = []
    for doc in registry.values():
        docs.append(DocumentResponse(
            id=doc["id"],
            filename=doc["filename"],
            document_type=doc.get("document_type", "policy"),
            page_count=doc.get("page_count", 0),
            chunk_count=doc.get("chunk_count"),
            uploaded_at=datetime.utcnow().isoformat(),
            status=doc.get("status", "ready"),
        ))
    return docs


@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    result = run_qa(
        question=request.question,
        document_ids=request.document_ids,
        session_id=request.session_id,
    )
    citations = [Citation(**c) for c in result.get("citations", [])]
    return AskResponse(
        answer=result["answer"],
        confidence=result["confidence"],
        citations=citations,
        evidence=result.get("evidence", ""),
        next_action=result.get("next_action", ""),
        session_id=result["session_id"],
        reasoning_steps=result.get("reasoning_steps", []),
        follow_up_questions=result.get("follow_up_questions", []),
        key_points=result.get("key_points", []),
        confidence_label=result.get("confidence_label", ""),
        recommended_action=result.get("recommended_action", result.get("next_action", "")),
        supporting_evidence=result.get("supporting_evidence", []),
    )


@router.post("/compare", response_model=CompareResponse)
async def compare_documents(request: CompareRequest):
    result = run_comparison(request.old_document_id, request.new_document_id)
    changes = [PolicyChange(**c) for c in result.get("changes", [])]
    return CompareResponse(
        summary=result["summary"],
        changes=changes,
        total_changes=result["total_changes"],
        high_risk_count=result["high_risk_count"],
        old_doc_name=result["old_doc_name"],
        new_doc_name=result["new_doc_name"],
    )


@router.post("/extract-rules", response_model=ExtractRulesResponse)
async def extract_rules(request: ExtractRulesRequest):
    result = run_rule_extraction(request.text, request.document_id)
    rules = [BusinessRule(**r) for r in result.get("rules", [])]
    return ExtractRulesResponse(
        rules=rules,
        document_id=result.get("document_id"),
        total_rules=result["total_rules"],
    )


@router.post("/extract-rules-from-document", response_model=ExtractRulesResponse)
async def extract_rules_from_document(request: ExtractRulesFromDocumentRequest):
    chunks = get_document_chunks(request.document_id)
    if not chunks:
        raise HTTPException(
            status_code=404,
            detail="No indexed chunks found for this document. Upload the document first.",
        )
    # Assemble text from up to 25 chunks, preserving page context
    text_parts = [
        f"[Page {c['page_number']}]\n{c['text']}"
        for c in chunks[:25]
    ]
    assembled_text = "\n\n---\n\n".join(text_parts)
    result = run_rule_extraction(assembled_text, request.document_id)
    rules = [BusinessRule(**r) for r in result.get("rules", [])]
    return ExtractRulesResponse(
        rules=rules,
        document_id=result.get("document_id"),
        total_rules=result["total_rules"],
    )


@router.post("/validate-claim", response_model=ClaimValidationResponse)
async def validate_claim(request: ClaimValidationRequest):
    result = run_claim_validation(request.model_dump())
    return ClaimValidationResponse(**result)


@router.get("/audit/{session_id}", response_model=AuditRecord)
async def get_audit_record(session_id: str):
    store = get_audit_store()
    record = store.get(session_id)
    if not record:
        raise HTTPException(status_code=404, detail="Audit record not found")
    return AuditRecord(
        session_id=record["session_id"],
        question=record["question"],
        retrieved_pages=record.get("retrieved_pages", []),
        reasoning_summary=record.get("reasoning_summary", ""),
        final_answer=record["final_answer"],
        confidence=record.get("confidence", 0.0),
        source_citations=[Citation(**c) for c in record.get("source_citations", [])],
        steps=[AuditStep(**s) for s in record.get("steps", [])],
        created_at=record["created_at"],
    )


@router.get("/audit", response_model=list[AuditRecord])
async def list_audit_records():
    store = get_audit_store()
    records = []
    for record in list(store.values())[:50]:
        records.append(AuditRecord(
            session_id=record["session_id"],
            question=record["question"],
            retrieved_pages=record.get("retrieved_pages", []),
            reasoning_summary=record.get("reasoning_summary", ""),
            final_answer=record["final_answer"],
            confidence=record.get("confidence", 0.0),
            source_citations=[Citation(**c) for c in record.get("source_citations", [])],
            steps=[AuditStep(**s) for s in record.get("steps", [])],
            created_at=record["created_at"],
        ))
    return records


@router.get("/claim-audit-records", response_model=list[ClaimAuditRecord])
async def list_claim_audit_records():
    store = get_claim_audit_store()
    records = []
    for r in list(store.values())[-100:]:  # last 100
        records.append(ClaimAuditRecord(
            audit_id=r.get("audit_id", ""),
            cpt_code=r.get("cpt_code", ""),
            diagnosis_code=r.get("diagnosis_code", ""),
            plan_type=r.get("plan_type", ""),
            procedure=r.get("procedure", ""),
            service_date=r.get("service_date", ""),
            decision=r.get("decision", ""),
            confidence=r.get("confidence", 0.0),
            rule_matched=r.get("rule_matched", False),
            created_at=r.get("created_at", ""),
        ))
    return records


@router.get("/stats", response_model=DashboardStats)
async def get_stats():
    registry = get_document_registry()
    audit = get_audit_store()
    claim_audit = get_claim_audit_store()
    rules_store = get_rules_store()

    confidences = [r.get("confidence", 0.0) for r in audit.values() if r.get("confidence", 0.0) > 0]
    avg_conf = sum(confidences) / len(confidences) if confidences else 0.0

    return DashboardStats(
        documents_uploaded=len(registry),
        questions_answered=len(audit),
        policy_changes_detected=0,
        rules_extracted=len(rules_store),
        claims_validated=len(claim_audit),
        avg_confidence=round(avg_conf, 3),
    )


@router.get("/sample-documents")
async def list_sample_documents():
    docs = []
    if SAMPLE_DOCS_DIR.exists():
        for f in sorted(SAMPLE_DOCS_DIR.glob("*.pdf")):
            docs.append({
                "filename": f.name,
                "label": _SAMPLE_LABELS.get(f.name, f.stem.replace("_", " ").title()),
                "size_kb": round(f.stat().st_size / 1024, 1),
            })
    return docs


@router.post("/load-sample")
async def load_sample_document(request: LoadSampleRequest):
    pdf_path = SAMPLE_DOCS_DIR / request.filename
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail=f"Sample document '{request.filename}' not found")

    file_bytes = pdf_path.read_bytes()
    result = run_intake(file_bytes, request.filename, "policy")
    if result.get("status") == "error":
        raise HTTPException(status_code=422, detail=result.get("error", "Processing failed"))
    return DocumentResponse(**result)


@router.post("/config/api-key")
async def configure_api_key(request: ApiKeyRequest):
    provider = request.provider.lower()
    if provider not in ("anthropic", "openai", "gemini"):
        raise HTTPException(status_code=400, detail="provider must be anthropic, openai, or gemini")
    if not request.api_key.strip():
        raise HTTPException(status_code=400, detail="api_key must not be empty")
    set_api_key(provider, request.api_key.strip())
    return {"status": "ok", "provider": provider, "message": f"{provider.title()} API key configured successfully"}


@router.get("/config/provider")
async def get_provider():
    return get_active_provider()


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "IntelliPolicy AI", "version": "1.0.0"}
