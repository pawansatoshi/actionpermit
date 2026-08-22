import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from .api import router

app = FastAPI(title="ActionPermit", version="1.0.0")
origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False, allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["*"])

@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    request_id = request.headers.get("X-Request-ID")
    if request_id:
        response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response

app.include_router(router)

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/readyz")
def readyz():
    return {"status": "ready"}

@app.get("/")
def root():
    return FileResponse(Path(__file__).resolve().parents[2] / "frontend" / "index.html")
