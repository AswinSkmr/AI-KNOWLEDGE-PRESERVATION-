from fastapi import FastAPI

app = FastAPI(title="Preserve AI")


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Preserve AI backend is running"}