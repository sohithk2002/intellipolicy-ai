"""Text chunking service — splits PDF pages into smaller semantic chunks."""
from dataclasses import dataclass
from .pdf_service import PageContent

CHUNK_SIZE    = 150   # words per chunk (was 512 — too large, collapsed many questions to same chunk)
CHUNK_OVERLAP = 25    # words overlap between adjacent chunks

@dataclass
class TextChunk:
    document_id:   str
    document_name: str
    page_number:   int
    chunk_index:   int
    text:          str


def chunk_pages(
    document_id:   str,
    document_name: str,
    pages:         list[PageContent],
    chunk_size:    int = CHUNK_SIZE,
    overlap:       int = CHUNK_OVERLAP,
) -> list[TextChunk]:
    chunks: list[TextChunk] = []

    for page in pages:
        words = page.text.split()
        if not words:
            continue

        start     = 0
        chunk_idx = 0
        while start < len(words):
            end         = start + chunk_size
            chunk_words = words[start:end]
            chunk_text  = " ".join(chunk_words)

            if len(chunk_text.strip()) > 20:
                chunks.append(TextChunk(
                    document_id   = document_id,
                    document_name = document_name,
                    page_number   = page.page_number,
                    chunk_index   = chunk_idx,
                    text          = chunk_text,
                ))
                chunk_idx += 1

            if end >= len(words):
                break
            start = end - overlap

    return chunks
