from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from auth import get_db
from deps import require_role
from document_service import FileValidationError, save_uploaded_document
from models import User
from schemas import DocumentRead

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