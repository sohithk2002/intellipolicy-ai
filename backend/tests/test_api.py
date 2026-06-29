"""
Integration tests for IntelliPolicy AI API endpoints.
Uses starlette.testclient (sync), no external services required for basic routes.
"""
import pytest
from starlette.testclient import TestClient


# ── Health ────────────────────────────────────────────────────────────────────

def test_health(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "healthy"
    assert body["service"] == "IntelliPolicy AI"
    assert "version" in body


# ── Stats ─────────────────────────────────────────────────────────────────────

def test_stats_shape(client: TestClient):
    r = client.get("/stats")
    assert r.status_code == 200
    body = r.json()
    expected_keys = {
        "documents_uploaded",
        "questions_answered",
        "policy_changes_detected",
        "rules_extracted",
        "claims_validated",
        "avg_confidence",
    }
    assert expected_keys.issubset(body.keys())
    assert isinstance(body["documents_uploaded"], int)
    assert isinstance(body["avg_confidence"], float)


# ── Documents ────────────────────────────────────────────────────────────────

def test_list_documents(client: TestClient):
    r = client.get("/documents")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_list_sample_documents(client: TestClient):
    r = client.get("/sample-documents")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


# ── Config / Provider ─────────────────────────────────────────────────────────

def test_get_provider(client: TestClient):
    r = client.get("/config/provider")
    assert r.status_code == 200
    body = r.json()
    assert "has_key" in body
    assert isinstance(body["has_key"], bool)


def test_set_api_key_invalid_provider(client: TestClient):
    r = client.post("/config/api-key", json={"provider": "fakeprovider", "api_key": "abc123"})
    assert r.status_code == 400


def test_set_api_key_empty_key(client: TestClient):
    r = client.post("/config/api-key", json={"provider": "anthropic", "api_key": ""})
    assert r.status_code == 400


def test_set_api_key_valid(client: TestClient):
    r = client.post("/config/api-key", json={"provider": "anthropic", "api_key": "sk-test-key-12345"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["provider"] == "anthropic"


# ── Audit ─────────────────────────────────────────────────────────────────────

def test_list_audit_records(client: TestClient):
    r = client.get("/audit")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_nonexistent_audit_record(client: TestClient):
    r = client.get("/audit/nonexistent-session-id")
    assert r.status_code == 404


# ── Claim Audit ───────────────────────────────────────────────────────────────

def test_list_claim_audit_records(client: TestClient):
    r = client.get("/claim-audit-records")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


# ── Claim Validation ──────────────────────────────────────────────────────────

def test_validate_claim_shape(client: TestClient):
    payload = {
        "cpt_code": "99213",
        "diagnosis_code": "Z00.00",
        "plan_type": "Medicare",
        "procedure": "Office visit established patient",
        "service_date": "2026-01-01",
    }
    r = client.post("/validate-claim", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["decision"] in ("Approved", "Denied", "Needs Review")
    assert isinstance(body["confidence"], float)
    assert 0.0 <= body["confidence"] <= 1.0
    assert isinstance(body["rule_matched"], bool)
    assert isinstance(body["missing_info"], list)
    assert isinstance(body["next_steps"], list)


def test_validate_claim_missing_required_fields(client: TestClient):
    r = client.post("/validate-claim", json={"cpt_code": "99213"})
    assert r.status_code == 422


# ── Rule Extraction ───────────────────────────────────────────────────────────

def test_extract_rules_empty_text(client: TestClient):
    r = client.post("/extract-rules", json={"text": "  "})
    # Should succeed (returning 0 rules) or return 422 — not 500
    assert r.status_code in (200, 422)


def test_extract_rules_from_nonexistent_document(client: TestClient):
    r = client.post("/extract-rules-from-document", json={"document_id": "nonexistent-doc-id"})
    assert r.status_code == 404


# ── Upload validation ─────────────────────────────────────────────────────────

def test_upload_non_pdf_rejected(client: TestClient):
    r = client.post(
        "/upload",
        files={"file": ("test.txt", b"hello world", "text/plain")},
        data={"document_type": "policy"},
    )
    assert r.status_code == 400


def test_load_nonexistent_sample(client: TestClient):
    r = client.post("/load-sample", json={"filename": "does_not_exist.pdf"})
    assert r.status_code == 404
