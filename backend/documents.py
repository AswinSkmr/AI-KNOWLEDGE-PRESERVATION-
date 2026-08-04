import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status, Path
from fastapi.responses import FileResponse

from sqlalchemy.orm import Session
from typing import Literal

from auth import get_db
from deps import require_role, get_current_user
from document_service import FileValidationError, save_uploaded_document, list_documents, process_document_text_extraction, generate_missing_summaries, get_summaries, generate_chunks_for_document, get_chunks
from document_service import (
    get_document_by_id,
    resolve_file_path,
    soft_delete_document,
    update_document,
)
from models import User
from schemas import DocumentRead, PaginatedDocuments, DocumentUpdate, DocumentExtractionResult, DocumentSummariesResponse, DocumentChunksResponse


router = APIRouter()


@router.post("/documents/upload", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document(
    title: str = Form(...),
    description: str | None = Form(None),
    document_type: str = Form(...),
    category: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "staff")),
):
    try:
        document = await save_uploaded_document(
            db=db,
            file=file,
            title=title,
            description=description,
            document_type=document_type,
            category=category,
            uploaded_by=current_user,
        )
    except FileValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return document


@router.get("/documents", response_model=PaginatedDocuments)
def get_documents(
    page: int = 1,
    page_size: int = 20,
    document_type: str | None = None,
    search: str | None = None,
    sort_by: str = "uploaded_at",
    sort_order: Literal["asc", "desc"] = "desc",
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 20

    return list_documents(
        db=db,
        page=page,
        page_size=page_size,
        document_type=document_type,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/documents/{document_id}", response_model=DocumentRead)
def get_document_detail(
    document_id: uuid.UUID = Path(...),
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return get_document_by_id(db, document_id)


@router.get("/documents/{document_id}/download")
def download_document(
    document_id: uuid.UUID = Path(...),
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    document = get_document_by_id(db, document_id)
    file_path = resolve_file_path(document)
    return FileResponse(
        path=file_path,
        media_type=document.mime_type,
        filename=document.original_file_name,
        content_disposition_type="attachment",
    )


@router.get("/documents/{document_id}/preview")
def preview_document(
    document_id: uuid.UUID = Path(...),
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    document = get_document_by_id(db, document_id)
    file_path = resolve_file_path(document)
    return FileResponse(
        path=file_path,
        media_type=document.mime_type,
        filename=document.original_file_name,
        content_disposition_type="inline",
    )


@router.patch("/documents/{document_id}", response_model=DocumentRead)
def edit_document(
    document_id: uuid.UUID,
    payload: DocumentUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    return update_document(db, document_id, payload)


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    soft_delete_document(db, document_id)


@router.post("/documents/{document_id}/extract-text", response_model=DocumentExtractionResult)
def extract_document_text(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    document = process_document_text_extraction(db, document_id)
    return DocumentExtractionResult(
        document_id=document.document_id,
        text_extraction_status=document.text_extraction_status,
        page_count=document.page_count,
        extraction_error=document.extraction_error,
        extracted_text_preview=(document.extracted_text[:500] if document.extracted_text else None),
    )



@router.get("/documents/{document_id}/summaries", response_model=DocumentSummariesResponse)
def get_document_summaries(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    summaries = get_summaries(db, document_id)
    return DocumentSummariesResponse(document_id=document_id, summaries=summaries)


@router.post("/documents/{document_id}/generate-summaries", response_model=DocumentSummariesResponse)
def create_document_summaries(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    summaries = generate_missing_summaries(db, document_id)
    return DocumentSummariesResponse(document_id=document_id, summaries=summaries)


@router.get("/documents/{document_id}/chunks", response_model=DocumentChunksResponse)
def get_document_chunks(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    chunks = get_chunks(db, document_id)
    return DocumentChunksResponse(document_id=document_id, chunk_count=len(chunks), chunks=chunks)


@router.post("/documents/{document_id}/generate-chunks", response_model=DocumentChunksResponse)
def create_document_chunks(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    chunks = generate_chunks_for_document(db, document_id)
    return DocumentChunksResponse(document_id=document_id, chunk_count=len(chunks), chunks=chunks)