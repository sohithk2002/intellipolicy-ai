from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class DocumentResponse(BaseModel):
    id: str
    filename: str
    document_type: str
    page_count: int
    chunk_count: Optional[int] = None
    uploaded_at: str
    status: str


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=2000)
    document_ids: Optional[list[str]] = None
    session_id: Optional[str] = None


class Citation(BaseModel):
    document_id: str
    document_name: str
    page_number: int
    text: str
    relevance_score: float


class AskResponse(BaseModel):
    answer: str
    confidence: float
    citations: list[Citation]
    evidence: str
    next_action: str
    session_id: str
    reasoning_steps: list[str]
    follow_up_questions: list[str] = []
    # structured fields — additive, never break existing consumers
    key_points: list[str] = []
    confidence_label: str = ""
    recommended_action: str = ""
    supporting_evidence: list[dict] = []


class CompareRequest(BaseModel):
    old_document_id: str
    new_document_id: str


class PolicyChange(BaseModel):
    area: str
    old_value: str
    new_value: str
    impact: str
    risk_level: str
    change_type: str


class CompareResponse(BaseModel):
    summary: str
    changes: list[PolicyChange]
    total_changes: int
    high_risk_count: int
    old_doc_name: str
    new_doc_name: str


class ExtractRulesRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=50000)
    document_id: Optional[str] = None


class ExtractRulesFromDocumentRequest(BaseModel):
    document_id: str


class BusinessRule(BaseModel):
    procedure: str
    cpt_code: Optional[str] = None
    icd_code: Optional[str] = None
    plan_type: str
    requires_prior_authorization: bool
    documentation_required: list[str]
    effective_date: Optional[str] = None
    authorization_timing: Optional[str] = None
    emergency_exception: Optional[str] = None
    source_page: Optional[int] = None
    confidence: float
    raw_text: str
    rule_type: Optional[str] = None
    actor: Optional[str] = None
    restriction: Optional[str] = None
    allowed_action: Optional[str] = None
    condition: Optional[str] = None


class ExtractRulesResponse(BaseModel):
    rules: list[BusinessRule]
    document_id: Optional[str] = None
    total_rules: int


class ClaimValidationRequest(BaseModel):
    cpt_code: str
    diagnosis_code: str
    plan_type: str
    procedure: str
    service_date: str
    provider_id: Optional[str] = None
    document_id: Optional[str] = None


class ClaimValidationResponse(BaseModel):
    decision: str  # "Approved" | "Denied" | "Needs Review"
    reason: str
    missing_info: list[str]
    policy_source: str
    source_page: Optional[int] = None
    confidence: float
    next_steps: list[str]
    rule_matched: bool = False
    document_fallback_performed: bool = False


class ClaimAuditRecord(BaseModel):
    audit_id: str
    cpt_code: str
    diagnosis_code: str
    plan_type: str
    procedure: str
    service_date: str
    decision: str
    confidence: float
    rule_matched: bool = False
    created_at: str


class AuditStep(BaseModel):
    step: str
    description: str
    timestamp: str
    data: Optional[dict] = None


class AuditRecord(BaseModel):
    session_id: str
    question: str
    retrieved_pages: list[int]
    reasoning_summary: str
    final_answer: str
    confidence: float = 0.0
    source_citations: list[Citation]
    steps: list[AuditStep]
    created_at: str


class DashboardStats(BaseModel):
    documents_uploaded: int
    questions_answered: int
    policy_changes_detected: int
    rules_extracted: int
    claims_validated: int = 0
    avg_confidence: float
