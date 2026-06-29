"""PDF extraction service using PyMuPDF."""
import fitz  # PyMuPDF
from dataclasses import dataclass
from typing import Optional
import re


@dataclass
class PageContent:
    page_number: int
    text: str
    char_count: int


@dataclass
class DocumentContent:
    filename: str
    page_count: int
    pages: list[PageContent]
    total_chars: int


def extract_pdf(file_bytes: bytes, filename: str) -> DocumentContent:
    """Extract text from PDF bytes, page by page."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages: list[PageContent] = []

    total_pages = len(doc)
    for page_num in range(total_pages):
        page = doc[page_num]
        text = page.get_text("text")
        text = _clean_text(text)
        if text.strip():
            pages.append(PageContent(
                page_number=page_num + 1,
                text=text,
                char_count=len(text),
            ))

    doc.close()
    return DocumentContent(
        filename=filename,
        page_count=total_pages,
        pages=pages,
        total_chars=sum(p.char_count for p in pages),
    )


def _clean_text(text: str) -> str:
    """Remove excessive whitespace and normalize text."""
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()
