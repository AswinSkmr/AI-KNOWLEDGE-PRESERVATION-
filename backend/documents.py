from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from typing import Literal

from auth import get_db
from deps import require_role, get_current_user
from document_service import FileValidationError, save_uploaded_document, list_documents
from models import User
from schemas import DocumentRead, PaginatedDocuments

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