from fastapi import FastAPI

from auth import router as auth_router
from users import router as users_router

app = FastAPI(title="Preserve AI")

app.include_router(auth_router)
app.include_router(users_router)



@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Preserve AI backend is running"}