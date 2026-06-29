export interface Document {
  id: string;
  filename: string;
  document_type: string;
  page_count: number;
  uploaded_at: string;
  status: "processing" | "ready" | "error";
  chunk_count?: number;
}

export interface AnswerCitation {
  document_id: string;
  document_name: string;
  page_number: number;
  text: string;
  relevance_score: number;
}

export interface AskResponse {
  answer: string;
  confidence: number;
  citations: AnswerCitation[];
  evidence: string;
  next_action: string;
  session_id: string;
  reasoning_steps: string[];
  follow_up_questions: string[];
}

export interface PolicyChange {
  area: string;
  old_value: string;
  new_value: string;
  impact: string;
  risk_level: "low" | "medium" | "high";
  change_type: string;
}

export interface CompareResponse {
  summary: string;
  changes: PolicyChange[];
  total_changes: number;
  high_risk_count: number;
  old_doc_name: string;
  new_doc_name: string;
}

export interface BusinessRule {
  procedure: string;
  cpt_code?: string;
  icd_code?: string;
  plan_type: string;
  requires_prior_authorization: boolean;
  documentation_required: string[];
  effective_date?: string;
  authorization_timing?: string;
  emergency_exception?: string;
  source_page: number | null;
  confidence: number;
  raw_text: string;
  rule_type?: string;
  actor?: string;
  restriction?: string;
  allowed_action?: string;
  condition?: string;
}

export interface ExtractRulesResponse {
  rules: BusinessRule[];
  document_id?: string;
  total_rules: number;
}

export interface ClaimValidationRequest {
  cpt_code: string;
  diagnosis_code: string;
  plan_type: string;
  procedure: string;
  service_date: string;
  provider_id?: string;
  document_id?: string;
}

export interface ClaimValidationResponse {
  decision: "Approved" | "Denied" | "Needs Review";
  reason: string;
  missing_info: string[];
  policy_source: string;
  source_page?: number;
  confidence: number;
  next_steps: string[];
  rule_matched: boolean;
  document_fallback_performed?: boolean;
}

export interface ClaimAuditRecord {
  audit_id: string;
  cpt_code: string;
  diagnosis_code: string;
  plan_type: string;
  procedure: string;
  service_date: string;
  decision: string;
  confidence: number;
  rule_matched: boolean;
  created_at: string;
}

export interface AuditStep {
  step: string;
  description: string;
  timestamp: string;
  data?: Record<string, unknown>;
}

export interface AuditRecord {
  session_id: string;
  question: string;
  retrieved_pages: number[];
  reasoning_summary: string;
  final_answer: string;
  confidence: number;
  source_citations: AnswerCitation[];
  steps: AuditStep[];
  created_at: string;
}
