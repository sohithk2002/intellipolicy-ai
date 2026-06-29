"""Vector store: PostgreSQL + PGVector with FAISS in-memory fallback."""
import os
import json
import logging
import numpy as np
from dataclasses import dataclass
from .embeddings import cosine_similarity

logger = logging.getLogger(__name__)


@dataclass
class RetrievedChunk:
    document_id: str
    document_name: str
    page_number: int
    text: str
    relevance_score: float


class InMemoryVectorStore:
    """Simple in-memory vector store when PGVector is not available."""

    def __init__(self):
        self._chunks: list[dict] = []

    def add_chunks(self, chunks_with_embeddings: list[dict]):
        self._chunks.extend(chunks_with_embeddings)

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        document_ids: list[str] | None = None,
    ) -> list[RetrievedChunk]:
        candidates = self._chunks
        if document_ids:
            candidates = [c for c in candidates if c["document_id"] in document_ids]

        scored = [
            (cosine_similarity(query_embedding, c["embedding"]), c)
            for c in candidates
        ]
        scored.sort(key=lambda x: x[0], reverse=True)

        results = []
        for score, chunk in scored[:top_k]:
            results.append(RetrievedChunk(
                document_id=chunk["document_id"],
                document_name=chunk["document_name"],
                page_number=chunk["page_number"],
                text=chunk["text"],
                relevance_score=round(score, 4),
            ))
        return results

    def document_exists(self, document_id: str) -> bool:
        return any(c["document_id"] == document_id for c in self._chunks)

    def get_all_chunks(self) -> list[dict]:
        return list(self._chunks)


class PGVectorStore:
    """PostgreSQL + PGVector store. Falls back to in-memory on connection error."""

    def __init__(self, db_session=None):
        self._db = db_session
        self._fallback = InMemoryVectorStore()
        self._use_pg = db_session is not None

    def add_chunks(self, chunks_with_embeddings: list[dict]):
        if not self._use_pg:
            self._fallback.add_chunks(chunks_with_embeddings)
            return

        try:
            from ..db.setup import ChunkRecord
            for chunk in chunks_with_embeddings:
                record = ChunkRecord(
                    id=chunk.get("id"),
                    document_id=chunk["document_id"],
                    document_name=chunk["document_name"],
                    page_number=chunk["page_number"],
                    text=chunk["text"],
                    chunk_index=chunk.get("chunk_index", 0),
                    embedding=chunk["embedding"],
                )
                self._db.merge(record)
            self._db.commit()
        except Exception as e:
            logger.warning(f"PGVector write failed, using in-memory: {e}")
            self._fallback.add_chunks(chunks_with_embeddings)

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        document_ids: list[str] | None = None,
    ) -> list[RetrievedChunk]:
        if not self._use_pg:
            return self._fallback.search(query_embedding, top_k, document_ids)

        try:
            from ..db.setup import ChunkRecord
            chunks = self._db.query(ChunkRecord)
            if document_ids:
                chunks = chunks.filter(ChunkRecord.document_id.in_(document_ids))
            all_chunks = chunks.all()

            scored = []
            for chunk in all_chunks:
                if chunk.embedding:
                    score = cosine_similarity(query_embedding, chunk.embedding)
                    scored.append((score, chunk))

            scored.sort(key=lambda x: x[0], reverse=True)
            return [
                RetrievedChunk(
                    document_id=c.document_id,
                    document_name=c.document_name,
                    page_number=c.page_number,
                    text=c.text,
                    relevance_score=round(s, 4),
                )
                for s, c in scored[:top_k]
            ]
        except Exception as e:
            logger.warning(f"PGVector search failed, using in-memory: {e}")
            return self._fallback.search(query_embedding, top_k, document_ids)


# Global in-memory store (used when DB is unavailable)
_global_store = InMemoryVectorStore()


def get_global_store() -> InMemoryVectorStore:
    return _global_store


def get_document_chunks(document_id: str) -> list[dict]:
    """Return all stored chunks for a given document_id."""
    return [c for c in _global_store._chunks if c["document_id"] == document_id]
