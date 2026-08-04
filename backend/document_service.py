import os
import uuid
import math
from datetime import datetime, timezone

from typing import Literal

from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc

from models import Document, User
from schemas import PaginatedDocuments

from ai.extractor import extract_text_from_pdf
from ai.summarizer import SummarizationError, generate_summary

ALLOWED_MIME_TYPES = {"application/pdf"}
ALLOWED_EXTENSION = ".pdf"

UPLOAD_DIRECTORY = os.getenv("UPLOAD_DIRECTORY", "uploads")
MAX_UPLOAD_SIZE_BYTES = int(os.getenv("MAX_UPLOAD_SIZE_MB", "20")) * 1024 * 1024


class FileValidationError(Exception):
    pass


def _validate_file(file: UploadFile, contents: bytes) -> None:
    if not file.filename.lower().endswith(ALLOWED_EXTENSION):
        raise FileValidationError("Only .pdf files are allowed")

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise FileValidationError("File must have MIME type application/pdf")

    if len(contents) > MAX_UPLOAD_SIZE_BYTES:
        raise FileValidationError(
            f"File exceeds maximum allowed size of {MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)} MB"
        )

    if not contents.startswith(b"%PDF-"):
        raise FileValidationError("File does not appear to be a valid PDF")


def _generate_safe_filename() -> str:
    return f"{uuid.uuid4()}{ALLOWED_EXTENSION}"


async def save_uploaded_document(
    db: Session,
    file: UploadFile,
    title: str,
    description: str | None,
    document_type: str,
    category: str | None,
    uploaded_by: User,
) -> Document:
    contents = await file.read()

    _validate_file(file, contents)

    safe_filename = _generate_safe_filename()
    os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
    save_path = os.path.join(UPLOAD_DIRECTORY, safe_filename)

    with open(save_path, "wb") as f:
        f.write(contents)

    document = Document(
        title=title,
        description=description,
        document_type=document_type,
        category=category,
        file_name=safe_filename,
        original_file_name=file.filename,
        file_path=save_path,
        file_size=len(contents),
        mime_type=file.content_type,
        uploaded_by=uploaded_by.id,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    return document


SORTABLE_COLUMNS = {
    "uploaded_at": Document.uploaded_at,
    "title": Document.title,
    "file_size": Document.file_size,
}


def list_documents(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    document_type: str | None = None,
    search: str | None = None,
    sort_by: str = "uploaded_at",
    sort_order: Literal["asc", "desc"] = "desc",
) -> PaginatedDocuments:
    query = db.query(Document).filter(Document.status == "active")

    if document_type:
        query = query.filter(Document.document_type == document_type)

    if search:
        query = query.filter(Document.title.ilike(f"%{search}%"))

    total = query.count()

    sort_column = SORTABLE_COLUMNS.get(sort_by, Document.uploaded_at)
    order_func = desc if sort_order == "desc" else asc
    query = query.order_by(order_func(sort_column))

    offset = (page - 1) * page_size
    documents = query.offset(offset).limit(page_size).all()

    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return PaginatedDocuments(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        documents=documents,
    )


def get_document_by_id(db: Session, document_id: uuid.UUID) -> Document:
    document = (
        db.query(Document)
        .filter(Document.document_id == document_id, Document.status == "active")
        .first()
    )
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


def update_document(db: Session, document_id: uuid.UUID, payload: "DocumentUpdate") -> Document:
    document = get_document_by_id(db, document_id)

    if payload.title is not None:
        document.title = payload.title
    if payload.description is not None:
        document.description = payload.description
    if payload.category is not None:
        document.category = payload.category

    db.commit()
    db.refresh(document)
    return document


def soft_delete_document(db: Session, document_id: uuid.UUID) -> None:
    document = get_document_by_id(db, document_id)
    document.status = "deleted"
    document.deleted_at = datetime.now(timezone.utc)
    db.commit()


def resolve_file_path(document: Document) -> str:
    if not os.path.isfile(document.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The file for this document is missing from storage",
        )
    return document.file_path


def process_document_text_extraction(db: Session, document_id: uuid.UUID) -> Document:
    document = get_document_by_id(db, document_id)

    result = extract_text_from_pdf(document.file_path)

    document.text_extraction_status = result.status
    document.extracted_text = result.text or None
    document.page_count = result.page_count
    document.extraction_error = result.error
    document.extracted_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(document)
    return document



SUMMARY_TYPES = ["short", "medium", "detailed"]
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")


def get_summaries(db: Session, document_id: uuid.UUID) -> list[DocumentSummary]:
    return (
        db.query(DocumentSummary)
        .filter(DocumentSummary.document_id == document_id)
        .all()
    )


def generate_missing_summaries(db: Session, document_id: uuid.UUID) -> list[DocumentSummary]:
    document = get_document_by_id(db, document_id)

    if not document.extracted_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This document has no extracted text. Run text extraction first.",
        )

    existing = get_summaries(db, document_id)
    existing_types = {s.summary_type for s in existing}
    missing_types = [t for t in SUMMARY_TYPES if t not in existing_types]

    if not missing_types:
        return existing

    for summary_type in missing_types:
        try:
            summary_text = generate_summary(document.extracted_text, summary_type)
        except SummarizationError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to generate {summary_type} summary: {exc}",
            )

        db.add(
            DocumentSummary(
                document_id=document_id,
                summary_type=summary_type,
                summary=summary_text,
                model_name=GEMINI_MODEL_NAME,
            )
        )

    db.commit()
    return get_summaries(db, document_id)