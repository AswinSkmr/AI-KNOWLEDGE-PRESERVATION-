# Preserve AI

**Preserve AI** is an AI-powered knowledge preservation platform for academic
institutions. It gives Admins, Staff, and Students a shared system for
managing user accounts and a growing knowledge repository of textbooks and
project reports — the foundation for AI-assisted summarization and search
planned in later weeks.

## Current Status

- ✅ Week 1 — Authentication foundation
- ✅ Week 2 — User Management Module
- ✅ Week 3 — Document Management Module
- ⏳ Week 4 — AI Summarization (planned)

## Tech Stack

**Backend**
- FastAPI — web framework
- SQLAlchemy (ORM) + Alembic (migrations)
- PostgreSQL — primary database
- JWT (`python-jose`) — stateless authentication
- Passlib (`bcrypt`) — password hashing

**Frontend**
- React (Vite)
- React Router — routing, including role-based protected routes
- Axios — HTTP client with a JWT-attaching interceptor
- Context API — global auth state

## Folder Structure

preserve-ai/
├── backend/
│ ├── .venv/ (gitignored)
│ ├── uploads/ (gitignored — uploaded PDFs live here)
│ ├── alembic/ Migration environment + versions
│ ├── main.py FastAPI app entry point, router registration
│ ├── database.py Engine, session factory, declarative Base
│ ├── models.py SQLAlchemy models: User, StudentProfile,
│ │ StaffProfile, Document
│ ├── schemas.py Pydantic request/response schemas
│ ├── security.py Password hashing + JWT encode/decode
│ ├── deps.py get_current_user, require_role
│ ├── auth.py /auth/login, get_db dependency
│ ├── users.py /users/* routes
│ ├── user_service.py User business logic
│ ├── staff.py /staff/* routes
│ ├── staff_service.py Staff business logic
│ ├── students.py /students/import route
│ ├── student_import_service.py CSV parsing + import logic
│ ├── documents.py /documents/* routes
│ ├── document_service.py File validation, storage,
│ │ listing, soft delete
│ ├── seed_admin.py Re-runnable admin seeding
│ ├── requirements.txt
│ └── .env.example
│
└── frontend/
└── src/
├── api.js Shared Axios instance + JWT interceptor
├── App.jsx Route definitions
├── context/
│ └── AuthContext.jsx Global auth state (Context API)
├── routes/
│ └── ProtectedRoute.jsx Auth + role-based route guard
└── pages/
├── LoginPage.jsx
├── DashboardPage.jsx
├── StaffDashboardPage.jsx
├── AdminUsersPage.jsx
├── AdminStaffPage.jsx
├── AdminStudentImportPage.jsx
├── DocumentUploadPage.jsx
├── DocumentListPage.jsx
└── DocumentDetailPage.jsx

### Architectural notes

- **Routes stay thin.** Business logic lives in `*_service.py` files
  (`user_service`, `staff_service`, `student_import_service`,
  `document_service`) — routes call into these rather than containing logic
  themselves.
- **`deps.py`** centralizes authorization: `get_current_user` decodes the JWT
  and loads the user (rejecting deactivated accounts too); `require_role(...)`
  is a dependency factory used across every role-gated route.
- **Frontend role checks are UX only.** The real security boundary is always
  the backend's `require_role(...)` — `ProtectedRoute` on the frontend just
  hides UI a user isn't allowed to use; it provides no actual protection on
  its own.
- **Soft delete, not hard delete**, for documents — a `status` column plus
  `deleted_at` timestamp preserve auditability rather than permanently
  removing records.

## Database Schema (current)

| Table | Purpose |
|---|---|
| `users` | Core account table — all roles (admin/staff/student), auth fields, `is_active` |
| `student_profiles` | 1:1 extension of `users` for student-specific fields |
| `staff_profiles` | 1:1 extension of `users` for staff-specific fields |
| `documents` | Uploaded PDF metadata — textbooks, project reports; soft-deletable |

## API Overview

**Auth**
- `POST /auth/login` — returns a JWT

**Users**
- `GET /users/me` — current user's own profile
- `GET /users` *(admin)* — list users, filterable by role
- `PATCH /users/{id}/activate` / `/deactivate` *(admin)*

**Staff**
- `GET /staff`, `POST /staff`, `PATCH /staff/{id}`, `PATCH /staff/{id}/disable` *(admin)*

**Students**
- `POST /students/import` *(admin)* — bulk CSV import with per-row results

**Documents**
- `POST /documents/upload` *(admin, staff)* — validated PDF upload
- `GET /documents` — paginated, searchable, filterable, sortable listing
- `GET /documents/{id}` — single document metadata
- `GET /documents/{id}/download`, `GET /documents/{id}/preview`
- `PATCH /documents/{id}` *(admin)* — edit title/description/category
- `DELETE /documents/{id}` *(admin)* — soft delete

## Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

copy .env.example .env        # Windows
# cp .env.example .env        # macOS/Linux
# Edit .env: set DATABASE_URL, SECRET_KEY (openssl rand -hex 32 or equivalent),
# UPLOAD_DIRECTORY, MAX_UPLOAD_SIZE_MB

createdb preserve_ai
alembic upgrade head

mkdir uploads

python seed_admin.py

uvicorn main:app --reload
```

API available at `http://localhost:8000`, interactive docs at `/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App available at `http://localhost:5173`.

### First login

Use the admin credentials seeded via `seed_admin.py` (`admin@test.com` /
`testpassword123` by default — check the script for current values).

## Coding Standards

- PEP 8, type hints throughout the backend
- Business logic in services, never in route handlers
- Dependency injection (FastAPI `Depends`) for DB sessions, current user, and
  role checks
- Every authorization rule is enforced on the backend first; frontend guards
  exist for UX, never as the sole protection

## Roadmap

- ✅ Authentication, role-based access
- ✅ User & Staff management, CSV student import
- ✅ Document upload, listing, detail, soft delete
- ⏳ AI-powered document summarization
- ⏳ Semantic search
- ⏳ Assignment upload + AI-assisted grading
- ⏳ Plagiarism detection
- ⏳ Staff analytics dashboard