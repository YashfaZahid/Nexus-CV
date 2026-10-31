"""PDF and DOCX content extraction."""

from __future__ import annotations

import io
from typing import BinaryIO

from docx import Document
from pypdf import PdfReader

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_BYTES_DEFAULT = 10 * 1024 * 1024


class DocumentParseError(Exception):
    pass


def validate_upload(filename: str, data: bytes, max_bytes: int = MAX_BYTES_DEFAULT) -> None:
    if not filename:
        raise DocumentParseError("No file selected.")
    lower = filename.lower()
    if not any(lower.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise DocumentParseError("Only PDF and DOCX files are supported.")
    if len(data) == 0:
        raise DocumentParseError("Uploaded file is empty.")
    if len(data) > max_bytes:
        mb = max_bytes / (1024 * 1024)
        raise DocumentParseError(f"File exceeds the {mb:.0f} MB size limit.")


def extract_text_from_pdf(data: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(data))
        parts: list[str] = []
        for page in reader.pages:
            text = page.extract_text() or ""
            if text.strip():
                parts.append(text.strip())
        content = "\n\n".join(parts).strip()
        if not content:
            raise DocumentParseError(
                "Could not extract text from this PDF. It may be scanned/image-only."
            )
        return content
    except DocumentParseError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise DocumentParseError(f"Failed to parse PDF: {exc}") from exc


def extract_text_from_docx(data: bytes) -> str:
    try:
        doc = Document(io.BytesIO(data))
        parts: list[str] = []
        for para in doc.paragraphs:
            if para.text.strip():
                parts.append(para.text.strip())
        for table in doc.tables:
            for row in table.rows:
                cells = [c.text.strip() for c in row.cells if c.text.strip()]
                if cells:
                    parts.append(" | ".join(cells))
        content = "\n".join(parts).strip()
        if not content:
            raise DocumentParseError("Could not extract text from this DOCX file.")
        return content
    except DocumentParseError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise DocumentParseError(f"Failed to parse DOCX: {exc}") from exc


def extract_text(filename: str, data: bytes, max_bytes: int = MAX_BYTES_DEFAULT) -> str:
    validate_upload(filename, data, max_bytes=max_bytes)
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return extract_text_from_pdf(data)
    if lower.endswith(".docx"):
        return extract_text_from_docx(data)
    raise DocumentParseError("Unsupported file type.")


def read_upload(file_obj: BinaryIO, filename: str, max_bytes: int = MAX_BYTES_DEFAULT) -> str:
    data = file_obj.read()
    return extract_text(filename, data, max_bytes=max_bytes)
