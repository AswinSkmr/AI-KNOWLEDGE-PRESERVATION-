import uuid

from sqlalchemy.orm import Session

from models import StaffProfile, User
from schemas import StaffCreate, StaffRead, StaffUpdate
from security import hash_password
from student_import_service import generate_temporary_password


def _to_staff_read(user: User) -> StaffRead:
    profile = user.staff_profile
    return StaffRead(
        id=user.id,
        university_id=user.university_id,
        full_name=user.full_name,
        email=user.email,
        is_active=user.is_active,
        department=profile.department if profile else None,
        designation=profile.designation if profile else None,
        employee_id=profile.employee_id if profile else None,
    )


def list_staff(db: Session) -> list[StaffRead]:
    users = db.query(User).filter(User.role == "staff").order_by(User.created_at.desc()).all()
    return [_to_staff_read(user) for user in users]


def create_staff(db: Session, payload: StaffCreate) -> tuple[StaffRead, str]:
    temp_password = generate_temporary_password()

    user = User(
        university_id=payload.university_id,
        full_name=payload.full_name,
        email=payload.email,
        password_hash=hash_password(temp_password),
        role="staff",
    )
    db.add(user)
    db.flush()

    profile = StaffProfile(
        user_id=user.id,
        department=payload.department,
        designation=payload.designation,
        employee_id=payload.employee_id,
    )
    db.add(profile)
    db.commit()
    db.refresh(user)

    return _to_staff_read(user), temp_password


def update_staff(db: Session, user_id: uuid.UUID, payload: StaffUpdate) -> StaffRead | None:
    user = db.query(User).filter(User.id == user_id, User.role == "staff").first()
    if user is None:
        return None

    if payload.full_name is not None:
        user.full_name = payload.full_name

    profile = user.staff_profile
    if profile is None:
        profile = StaffProfile(user_id=user.id)
        db.add(profile)

    if payload.department is not None:
        profile.department = payload.department
    if payload.designation is not None:
        profile.designation = payload.designation
    if payload.employee_id is not None:
        profile.employee_id = payload.employee_id

    db.commit()
    db.refresh(user)
    return _to_staff_read(user)