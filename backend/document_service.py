import os
import uuid
import math
from typing import Literal

from fastapi import UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc

from models import Document, User
from schemas import PaginatedDocuments

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