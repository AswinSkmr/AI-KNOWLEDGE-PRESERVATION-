import csv
import io
import secrets

from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models import StudentProfile, User
from schemas import ImportRowResult, ImportSummary, StudentCsvRow
from security import hash_password

REQUIRED_COLUMNS = {"university_id", "full_name", "email"}


def generate_temporary_password() -> str:
    return secrets.token_urlsafe(9)


def _user_exists(db: Session, email: str, university_id: str) -> bool:
    return (
        db.query(User)
        .filter((User.email == email) | (User.university_id == university_id))
        .first()
        is not None
    )


def import_students_from_csv(db: Session, file_contents: bytes) -> ImportSummary:
    text = file_contents.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))

    if reader.fieldnames is None or not REQUIRED_COLUMNS.issubset(set(reader.fieldnames)):
        raise ValueError(
            f"CSV must include columns: {', '.join(sorted(REQUIRED_COLUMNS))}"
        )

    results: list[ImportRowResult] = []

    for row_number, raw_row in enumerate(reader, start=2):  # row 1 is the header
        try:
            row = StudentCsvRow(**raw_row)
        except ValidationError as exc:
            results.append(
                ImportRowResult(
                    row_number=row_number,
                    status="error",
                    email=raw_row.get("email"),
                    detail=f"Invalid row: {exc.errors()[0]['msg']}",
                )
            )
            continue

        if _user_exists(db, row.email, row.university_id):
            results.append(
                ImportRowResult(
                    row_number=row_number,
                    status="skipped",
                    email=row.email,
                    detail="A user with this email or university ID already exists",
                )
            )
            continue

        temp_password = generate_temporary_password()

        try:
            with db.begin_nested():
                user = User(
                    university_id=row.university_id,
                    full_name=row.full_name,
                    email=row.email,
                    password_hash=hash_password(temp_password),
                    role="student",
                )
                db.add(user)
                db.flush()  # makes user.id available without ending the savepoint

                profile = StudentProfile(
                    user_id=user.id,
                    department=row.department,
                    batch_year=row.batch_year,
                    semester=row.semester,
                )
                db.add(profile)

            results.append(
                ImportRowResult(
                    row_number=row_number,
                    status="created",
                    email=row.email,
                    detail="Account created",
                    temporary_password=temp_password,
                )
            )
        except IntegrityError:
            results.append(
                ImportRowResult(
                    row_number=row_number,
                    status="error",
                    email=row.email,
                    detail="Database error — row skipped",
                )
            )

    db.commit()

    created = sum(1 for r in results if r.status == "created")
    skipped = sum(1 for r in results if r.status == "skipped")
    errors = sum(1 for r in results if r.status == "error")

    return ImportSummary(
        total_rows=len(results),
        created_count=created,
        skipped_count=skipped,
        error_count=errors,
        results=results,
    )