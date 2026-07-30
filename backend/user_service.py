import uuid

from sqlalchemy.orm import Session

from models import User


def get_users(db: Session, role: str | None = None) -> list[User]:
    query = db.query(User)
    if role is not None:
        query = query.filter(User.role == role)
    return query.order_by(User.created_at.desc()).all()


def set_user_active_status(db: Session, user_id: uuid.UUID, is_active: bool) -> User | None:
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        return None

    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user