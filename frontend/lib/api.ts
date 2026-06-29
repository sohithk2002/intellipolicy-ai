import {
  AskResponse,
  ClaimValidationRequest,
  ClaimValidationResponse,
  CompareResponse,
  Document,
  ExtractRulesResponse,
  AuditRecord,
  ClaimAuditRecord,
} from "./types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchAPI<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export interface SampleDocument {
  filename: string;
  label: string;
  size_kb: number;
}

export const api = {
  async uploadDocument(file: File, documentType = "policy"): Promise<Document> {
    const form = new FormData();
    form.append("file", file);
    form.append("document_type", documentType);
    const res = await fetch(`${BASE_URL}/upload`, { method: "POST", body: form });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Upload failed" }));
      throw new Error(err.detail || "Upload failed");
    }
    return res.json();
  },

  async getDocuments(): Promise<Document[]> {
    return fetchAPI<Document[]>("/documents");
  },

  async getSampleDocuments(): Promise<SampleDocument[]> {
    return fetchAPI<SampleDocument[]>("/sample-documents");
  },

  async loadSampleDocument(filename: string): Promise<Document> {
    return fetchAPI<Document>("/load-sample", {
      method: "POST",
      body: JSON.stringify({ filename }),
    });
  },

  async setApiKey(provider: string, apiKey: string): Promise<{ status: string; message: string }> {
    return fetchAPI("/config/api-key", {
      method: "POST",
      body: JSON.stringify({ provider, api_key: apiKey }),
    });
  },

  async getActiveProvider(): Promise<{ provider: string | null; has_key: boolean }> {
    return fetchAPI("/config/provider");
  },

  async askQuestion(
    question: string,
    documentIds?: string[],
    sessionId?: string
  ): Promise<AskResponse> {
    return fetchAPI<AskResponse>("/ask", {
      method: "POST",
      body: JSON.stringify({ question, document_ids: documentIds, session_id: sessionId }),
    });
  },

  async compareDocuments(oldDocId: string, newDocId: string): Promise<CompareResponse> {
    return fetchAPI<CompareResponse>("/compare", {
      method: "POST",
      body: JSON.stringify({ old_document_id: oldDocId, new_document_id: newDocId }),
    });
  },

  async extractRules(text: string, documentId?: string): Promise<ExtractRulesResponse> {
    return fetchAPI<ExtractRulesResponse>("/extract-rules", {
      method: "POST",
      body: JSON.stringify({ text, document_id: documentId }),
    });
  },

  async extractRulesFromDocument(documentId: string): Promise<ExtractRulesResponse> {
    return fetchAPI<ExtractRulesResponse>("/extract-rules-from-document", {
      method: "POST",
      body: JSON.stringify({ document_id: documentId }),
    });
  },

  async validateClaim(data: ClaimValidationRequest): Promise<ClaimValidationResponse> {
    return fetchAPI<ClaimValidationResponse>("/validate-claim", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async getAuditRecord(sessionId: string): Promise<AuditRecord> {
    return fetchAPI<AuditRecord>(`/audit/${sessionId}`);
  },

  async getAuditRecords(): Promise<AuditRecord[]> {
    return fetchAPI<AuditRecord[]>("/audit");
  },

  async getClaimAuditRecords(): Promise<ClaimAuditRecord[]> {
    return fetchAPI<ClaimAuditRecord[]>("/claim-audit-records");
  },

  async getDashboardStats() {
    return fetchAPI<{
      documents_uploaded: number;
      questions_answered: number;
      policy_changes_detected: number;
      rules_extracted: number;
      claims_validated: number;
      avg_confidence: number;
    }>("/stats");
  },
};
