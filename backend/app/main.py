import os
from pathlib import Path
from uuid import uuid4
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from .api import router

app = FastAPI(title="ActionPermit", version="0.3.0")
allowed_origins = [x.strip() for x in os.getenv("ALLOWED_ORIGINS", "*").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=allowed_origins, allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["Content-Type", "X-Request-ID"])
app.include_router(router)
FRONTEND = Path(__file__).resolve().parents[2] / "frontend"


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


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
