"""Retrieval Agent — semantic vector search over indexed chunks."""
import logging
from ..services.embeddings import embed_query
from ..services.vector_store import get_global_store, RetrievedChunk

logger = logging.getLogger(__name__)


def run_retrieval(
    query: str,
    top_k: int = 5,
    document_ids: list[str] | None = None,
) -> list[RetrievedChunk]:
    """Embed the query and retrieve the top-k relevant chunks."""
    logger.info(f"[RetrievalAgent] Query: {query[:80]}...")
    query_embedding = embed_query(query)
    store = get_global_store()
    results = store.search(query_embedding, top_k=top_k, document_ids=document_ids)
    logger.info(f"[RetrievalAgent] Retrieved {len(results)} chunks")
    return results
