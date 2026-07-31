import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from auth import get_db
from deps import require_role
from models import User
from schemas import StaffCreate, StaffCreateResponse, StaffRead, StaffUpdate
from staff_service import create_staff, list_staff, update_staff
from user_service import set_user_active_status

router = APIRouter()


@router.get("/staff", response_model=list[StaffRead])
def get_staff_list(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    return list_staff(db)


@router.post("/staff", response_model=StaffCreateResponse, status_code=status.HTTP_201_CREATED)
def add_staff(
    payload: StaffCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    try:
        staff, temp_password = create_staff(db, payload)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email or university ID already exists",
        )
    return StaffCreateResponse(staff=staff, temporary_password=temp_password)


@router.patch("/staff/{user_id}", response_model=StaffRead)
def edit_staff(
    user_id: uuid.UUID,
    payload: StaffUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    staff = update_staff(db, user_id, payload)
    if staff is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff member not found")
    return staff


@router.patch("/staff/{user_id}/disable", response_model=StaffRead)
def disable_staff(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    user = set_user_active_status(db, user_id, is_active=False)
    if user is None or user.role != "staff":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff member not found")
    return _staff_read_after_disable(db, user_id)


def _staff_read_after_disable(db: Session, user_id: uuid.UUID) -> StaffRead:
    from staff_service import _to_staff_read

    user = db.query(User).filter(User.id == user_id).first()
    return _to_staff_read(user)