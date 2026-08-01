import os
import uuid

from fastapi import UploadFile
from sqlalchemy.orm import Session

from models import Document, User

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