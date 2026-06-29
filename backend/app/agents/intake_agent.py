"""Intake Agent — reads PDF, extracts text, stores metadata and chunks."""
import uuid
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from ..services.pdf_service import extract_pdf
from ..services.chunker import chunk_pages
from ..services.embeddings import embed_texts
from ..services.vector_store import get_global_store

logger = logging.getLogger(__name__)

_document_registry: dict[str, dict] = {}

_STORE_FILE = Path(__file__).resolve().parent.parent.parent / ".doc_store.json"


@dataclass
class IntakeState:
    document_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    filename: str = ""
    document_type: str = "policy"
    file_bytes: bytes = b""
    page_count: int = 0
    chunk_count: int = 0
    status: str = "pending"
    error: Optional[str] = None


# ── Persistence helpers ───────────────────────────────────────────────────────

def _save_doc_store() -> None:
    """Persist document registry + vector store chunks to disk after every upload."""
    try:
        store = get_global_store()
        data = {
            "registry": _document_registry,
            "chunks": store.get_all_chunks(),
        }
        _STORE_FILE.write_text(json.dumps(data))
        logger.info(
            f"[IntakeAgent] Saved doc store: {len(_document_registry)} docs, "
            f"{len(data['chunks'])} chunks"
        )
    except Exception as e:
        logger.warning(f"[IntakeAgent] Could not save doc store: {e}")


def _load_doc_store() -> None:
    """Restore document registry + vector store from disk on startup."""
    try:
        if not _STORE_FILE.exists():
            return
        data = json.loads(_STORE_FILE.read_text())
        registry: dict = data.get("registry", {})
        chunks: list = data.get("chunks", [])
        if not registry:
            return
        _document_registry.update(registry)
        if chunks:
            get_global_store().add_chunks(chunks)
        logger.info(
            f"[IntakeAgent] Restored doc store: {len(registry)} docs, {len(chunks)} chunks"
        )
    except Exception as e:
        logger.warning(f"[IntakeAgent] Could not load doc store: {e}")


_load_doc_store()


# ── Core intake pipeline ──────────────────────────────────────────────────────

def run_intake(file_bytes: bytes, filename: str, document_type: str = "policy") -> dict:
    """Execute the intake pipeline: extract → chunk → embed → store → persist."""
    state = IntakeState(filename=filename, document_type=document_type, file_bytes=file_bytes)
    logger.info(f"[IntakeAgent] Processing {filename} ({len(file_bytes)} bytes)")

    # Step 1: Extract text from PDF
    try:
        doc_content = extract_pdf(file_bytes, filename)
        state.page_count = doc_content.page_count
        logger.info(f"[IntakeAgent] Extracted {len(doc_content.pages)} pages")
    except Exception as e:
        state.status = "error"
        state.error = f"PDF extraction failed: {e}"
        return _to_response(state)

    # Step 2: Chunk pages
    chunks = chunk_pages(state.document_id, filename, doc_content.pages)
    state.chunk_count = len(chunks)
    logger.info(f"[IntakeAgent] Created {len(chunks)} chunks")

    # Step 3: Embed chunks
    chunk_texts = [c.text for c in chunks]
    try:
        embeddings = embed_texts(chunk_texts)
    except Exception as e:
        logger.warning(f"[IntakeAgent] Embedding failed: {e}, using zero vectors")
        embeddings = [[0.0] * 384] * len(chunks)

    # Step 4: Store in vector store
    store = get_global_store()
    chunks_with_embeddings = [
        {
            "id": str(uuid.uuid4()),
            "document_id": state.document_id,
            "document_name": filename,
            "page_number": c.page_number,
            "chunk_index": c.chunk_index,
            "text": c.text,
            "embedding": embeddings[i],
        }
        for i, c in enumerate(chunks)
    ]
    store.add_chunks(chunks_with_embeddings)

    # Register document metadata
    state.status = "ready"
    _document_registry[state.document_id] = {
        "id": state.document_id,
        "filename": filename,
        "document_type": document_type,
        "page_count": state.page_count,
        "chunk_count": state.chunk_count,
        "status": "ready",
    }

    logger.info(f"[IntakeAgent] Done: {state.document_id}")

    # Step 5: Persist to disk so uploads survive backend restarts
    _save_doc_store()

    return _to_response(state)


def _to_response(state: IntakeState) -> dict:
    from datetime import datetime
    return {
        "id": state.document_id,
        "filename": state.filename,
        "document_type": state.document_type,
        "page_count": state.page_count,
        "chunk_count": state.chunk_count,
        "status": state.status,
        "uploaded_at": datetime.utcnow().isoformat(),
    }


def get_document_registry() -> dict[str, dict]:
    return _document_registry
