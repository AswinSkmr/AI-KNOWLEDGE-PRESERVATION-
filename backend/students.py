from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from auth import get_db
from deps import require_role
from models import User
from schemas import ImportSummary
from student_import_service import import_students_from_csv

router = APIRouter()


@router.post("/students/import", response_model=ImportSummary)
async def import_students(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a .csv file",
        )

    contents = await file.read()

    try:
        return import_students_from_csv(db, contents)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))