import uuid

from sqlalchemy import Column, String, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base
https://github.com/AswinSkmr/AI-KNOWLEDGE-PRESERVATION-

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student_profile = relationship(
        "StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    staff_profile = relationship(
        "StaffProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    department = Column(String(120), nullable=True)
    batch_year = Column(String(20), nullable=True)
    semester = Column(String(20), nullable=True)
    roll_number = Column(String(50), nullable=True)

    user = relationship("User", back_populates="student_profile")


class StaffProfile(Base):
    __tablename__ = "staff_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    department = Column(String(120), nullable=True)
    designation = Column(String(120), nullable=True)
    employee_id = Column(String(50), nullable=True)

    user = relationship("User", back_populates="staff_profile")