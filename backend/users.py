import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import get_db
from deps import get_current_user, require_role
from models import User
from schemas import UserRead
from user_service import get_users, set_user_active_status

router = APIRouter()


@router.get("/users/me")
def read_current_user(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "full_name": current_user.full_name,
        "email": current_user.email,
        "role": current_user.role,
    }


@router.get("/users/admin-only")
def admin_only_route(current_user: User = Depends(require_role("admin"))):
    return {"message": f"Welcome, admin {current_user.full_name}"}


@router.get("/users", response_model=list[UserRead])
def list_users(
    role: str | None = None,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    return get_users(db, role=role)


@router.patch("/users/{user_id}/activate", response_model=UserRead)
def activate_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    user = set_user_active_status(db, user_id, is_active=True)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch("/users/{user_id}/deactivate", response_model=UserRead)
def deactivate_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")),
):
    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own account",
        )

    user = set_user_active_status(db, user_id, is_active=False)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user