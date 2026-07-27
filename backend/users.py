from fastapi import APIRouter, Depends

from deps import get_current_user, require_role
from models import User

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