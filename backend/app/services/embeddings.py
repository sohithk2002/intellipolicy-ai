"""Embedding service using HuggingFace sentence-transformers with FAISS fallback."""
import os
import logging
import numpy as np
from typing import Optional

logger = logging.getLogger(__name__)

_model = None
_model_name = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        logger.info(f"Loading embedding model: {_model_name}")
        _model = SentenceTransformer(_model_name)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of texts, returning 384-dim float vectors."""
    model = _get_model()
    embeddings = model.encode(texts, normalize_embeddings=True, batch_size=32, show_progress_bar=False)
    return embeddings.tolist()


def embed_query(query: str) -> list[float]:
    """Embed a single query string."""
    return embed_texts([query])[0]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    va = np.array(a)
    vb = np.array(b)
    norm_a = np.linalg.norm(va)
    norm_b = np.linalg.norm(vb)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(va, vb) / (norm_a * norm_b))
