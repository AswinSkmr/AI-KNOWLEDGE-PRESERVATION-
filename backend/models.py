import uuid

from sqlalchemy import Column, String, DateTime, func, ForeignKey, Boolean, Text, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(150), nullable=False)
    university_id = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True, server_default="true")
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


class Document(Base):
    __tablename__ = "documents"

    document_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    document_type = Column(String(50), nullable=False, index=True)
    category = Column(String(100), nullable=True, index=True)

    file_name = Column(String(255), nullable=False)
    original_file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    extracted_text = Column(Text, nullable=True)
    text_extraction_status = Column(
        String(20), nullable=False, default="pending", server_default="pending"
    )
    page_count = Column(Integer, nullable=True)
    extraction_error = Column(Text, nullable=True)
    extracted_at = Column(DateTime(timezone=True), nullable=True)
    uploaded_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), nullable=False, default="active", server_default="active")

    uploader = relationship("User")