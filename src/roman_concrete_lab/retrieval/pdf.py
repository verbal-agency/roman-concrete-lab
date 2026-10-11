"""Page-aware, non-executing extraction for lawfully public PDFs."""

from __future__ import annotations

import hashlib
import re
from io import BytesIO
from typing import Any

from pypdf import PdfReader

from .contracts import PolicyBlocked


class DocumentExtractionError(RuntimeError):
    """The permitted document cannot be parsed with the frozen extractor."""


PARSER_ID = "pypdf-6.20.0-page-text"


def _hash(value: str | bytes) -> str:
    payload = value if isinstance(value, bytes) else value.encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def extract_pdf(
    payload: bytes,
    *,
    locator: str,
    max_pages: int,
    max_characters: int,
) -> dict[str, Any]:
    """Return page-located text only; PDFs never execute embedded actions/code."""
    try:
        reader = PdfReader(BytesIO(payload), strict=False)
        if reader.is_encrypted:
            if reader.decrypt("") == 0:
                raise PolicyBlocked("encrypted PDF requires credentials and is outside policy")
    except PolicyBlocked:
        raise
    except Exception as exc:
        raise DocumentExtractionError(f"PDF reader rejected document: {type(exc).__name__}: {exc}") from exc
    if len(reader.pages) > max_pages:
        raise PolicyBlocked(f"PDF page count {len(reader.pages)} exceeds frozen limit {max_pages}")
    pages = []
    used = 0
    for number, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text(extraction_mode="layout") or ""
        except Exception:
            text = page.extract_text() or ""
        text = re.sub(r"[\t ]+", " ", text).strip()
        if used + len(text) > max_characters:
            text = text[: max(0, max_characters - used)]
            status = "PARTIAL"
        else:
            status = "EXTRACTED"
        used += len(text)
        pages.append(
            {
                "page_number": number,
                "locator": f"{locator}#page={number}",
                "text": text,
                "text_hash": _hash(text),
                "text_characters": len(text),
                "status": "OCR_REQUIRED" if not text else status,
            }
        )
        if used >= max_characters:
            break
    status = "PARTIAL" if len(pages) < len(reader.pages) or any(page["status"] == "PARTIAL" for page in pages) else "EXTRACTED"
    if pages and all(page["status"] == "OCR_REQUIRED" for page in pages):
        status = "OCR_REQUIRED"
    return {
        "content_hash": _hash(payload),
        "content_type": "application/pdf",
        "parser": PARSER_ID,
        "page_count": len(reader.pages),
        "extraction_status": status,
        "pages": pages,
    }


def select_relevant_page_spans(
    document: dict[str, Any],
    *,
    question: str,
    title: str,
    max_characters: int,
) -> list[dict[str, Any]]:
    """Select bounded, page-located input spans without making semantic claims."""
    terms = set(re.findall(r"[a-z0-9]{4,}", f"{question} {title}".lower()))
    structural = {"abstract", "materials", "method", "methods", "results", "discussion", "table", "figure", "conclusion"}
    ranked = []
    for page in document["pages"]:
        text = page["text"]
        tokens = set(re.findall(r"[a-z0-9]{4,}", text.lower()))
        score = len(terms.intersection(tokens)) * 3 + len(structural.intersection(tokens))
        # The first page is useful for bibliographic identity/abstract even
        # when query terms are absent from a scanned title page.
        if page["page_number"] == 1:
            score += 1
        ranked.append((score, page["page_number"], page))
    selected = []
    used = 0
    for _, _, page in sorted(ranked, key=lambda item: (-item[0], item[1])):
        if not page["text"]:
            continue
        remaining = max_characters - used
        if remaining <= 0:
            break
        text = page["text"][:remaining]
        # Facts bind to the full extracted page hash even when the mapper sees
        # only a bounded excerpt.  The excerpt hash is diagnostic only.
        selected.append({**page, "text": text, "excerpt_text_hash": _hash(text)})
        used += len(text)
    return sorted(selected, key=lambda item: item["page_number"])
