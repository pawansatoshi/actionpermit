from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from .api import router

app = FastAPI(title="ActionPermit", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["Content-Type", "X-Request-ID"])
app.include_router(router)
FRONTEND = Path(__file__).resolve().parents[2] / "frontend"

@app.get("/healthz", tags=["health"])
def healthz():
    return {"status": "ok"}

@app.get("/readyz", tags=["health"])
def readyz():
    return {"status": "ready"}

@app.get("/", include_in_schema=False)
def index():
    return FileResponse(FRONTEND / "index.html")

@app.get("/styles.css", include_in_schema=False)
def styles():
    return FileResponse(FRONTEND / "styles.css", media_type="text/css")

@app.get("/app.js", include_in_schema=False)
def javascript():
    return FileResponse(FRONTEND / "app.js", media_type="application/javascript")
