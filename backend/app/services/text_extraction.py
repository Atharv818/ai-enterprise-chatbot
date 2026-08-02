import fitz  # PyMuPDF
from docx import Document as DocxDocument

from app.core.logging_config import get_logger

logger = get_logger(__name__)


def extract_text(storage_path: str, file_type: str) -> str:
    """
    Extracts raw text from a PDF, DOCX, or TXT file.
    Returns the full text as a single string.
    """
    if file_type == "pdf":
        return _extract_pdf(storage_path)
    elif file_type == "docx":
        return _extract_docx(storage_path)
    elif file_type == "txt":
        return _extract_txt(storage_path)
    else:
        raise ValueError(f"Unsupported file type for text extraction: {file_type}")


def _extract_pdf(path: str) -> str:
    text_parts = []
    with fitz.open(path) as doc:
        for page in doc:
            text_parts.append(page.get_text())
    return "\n".join(text_parts)


def _extract_docx(path: str) -> str:
    doc = DocxDocument(path)
    return "\n".join(p.text for p in doc.paragraphs)


def _extract_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()
    
    