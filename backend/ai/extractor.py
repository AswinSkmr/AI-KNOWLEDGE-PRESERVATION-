"""PDF text extraction and cleaning, using PyMuPDF (fitz)."""
import logging
import os
import re
from dataclasses import dataclass

import fitz

logger = logging.getLogger("preserve_ai.ai")

MAX_PAGES = int(os.getenv("MAX_PDF_PAGES", "500"))
SCANNED_TEXT_THRESHOLD = 20  # avg characters/page below this suggests an image-only PDF


@dataclass
class ExtractionResult:
    status: str  # "completed" | "empty" | "likely_scanned" | "failed"
    text: str
    page_count: int
    error: str | None = None


def clean_text(text: str) -> str:
    text = text.replace("\x00", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_text_from_pdf(file_path: str) -> ExtractionResult:
    try:
        doc = fitz.open(file_path)
    except Exception as exc:
        logger.warning("Failed to open PDF %s: %s", file_path, exc)
        return ExtractionResult(status="failed", text="", page_count=0, error=str(exc))

    try:
        page_count = doc.page_count

        if page_count == 0:
            return ExtractionResult(
                status="failed", text="", page_count=0, error="PDF contains no pages"
            )

        pages_to_read = min(page_count, MAX_PAGES)
        if page_count > MAX_PAGES:
            logger.warning(
                "PDF %s has %d pages; only reading first %d", file_path, page_count, MAX_PAGES
            )

        page_texts = [doc.load_page(i).get_text("text") for i in range(pages_to_read)]
        full_text = clean_text("\n\n".join(page_texts))

    except Exception as exc:
        logger.error("Error reading pages from %s: %s", file_path, exc)
        return ExtractionResult(status="failed", text="", page_count=0, error=str(exc))
    finally:
        doc.close()

    if not full_text:
        return ExtractionResult(status="empty", text="", page_count=page_count)

    avg_chars_per_page = len(full_text) / pages_to_read
    if avg_chars_per_page < SCANNED_TEXT_THRESHOLD:
        return ExtractionResult(
            status="likely_scanned",
            text=full_text,
            page_count=page_count,
            error="Very little text found per page — this PDF may be scanned images requiring OCR",
        )

    return ExtractionResult(status="completed", text=full_text, page_count=page_count)