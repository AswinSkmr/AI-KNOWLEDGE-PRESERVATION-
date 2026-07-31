from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from auth import router as auth_router
from users import router as users_router
from students import router as students_router
from staff import router as staff_router



app = FastAPI(title="Preserve AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(students_router)
app.include_router(staff_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Preserve AI backend is running"}