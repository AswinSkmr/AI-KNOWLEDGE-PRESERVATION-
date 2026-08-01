import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict, field_validator


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime


class StudentCsvRow(BaseModel):
    university_id: str
    full_name: str
    email: EmailStr
    department: str | None = None
    batch_year: str | None = None
    semester: str | None = None

    @field_validator("university_id", "full_name")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("must not be blank")
        return value.strip()


class ImportRowResult(BaseModel):
    row_number: int
    status: str  # "created" | "skipped" | "error"
    email: str | None = None
    detail: str
    temporary_password: str | None = None


class ImportSummary(BaseModel):
    total_rows: int
    created_count: int
    skipped_count: int
    error_count: int
    results: list[ImportRowResult]


class StaffCreate(BaseModel):
    university_id: str
    full_name: str
    email: EmailStr
    department: str | None = None
    designation: str | None = None
    employee_id: str | None = None


class StaffUpdate(BaseModel):
    full_name: str | None = None
    department: str | None = None
    designation: str | None = None
    employee_id: str | None = None


class StaffRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    university_id: str
    full_name: str
    email: str
    is_active: bool
    department: str | None = None
    designation: str | None = None
    employee_id: str | None = None


class StaffCreateResponse(BaseModel):
    staff: StaffRead
    temporary_password: str


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_id: uuid.UUID
    title: str
    description: str | None = None
    document_type: str
    category: str | None = None
    original_file_name: str
    file_size: int
    mime_type: str
    uploaded_by: uuid.UUID
    uploaded_at: datetime
    status: str


class PaginatedDocuments(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    documents: list[DocumentRead]