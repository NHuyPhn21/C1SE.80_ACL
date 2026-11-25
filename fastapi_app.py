"""ACL FastAPI application entry point."""

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.api import router
from backend.image_utils import BASE_DIR

_default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5000",
    "http://127.0.0.1:5000",
]
_extra_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
]

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
FRONTEND_DIST_DIR = BASE_DIR / "frontend" / "dist"

app = FastAPI(title="Automated Comic Localization API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[*_default_origins, *_extra_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/media", StaticFiles(directory=DATA_DIR), name="media")
app.include_router(router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


if (FRONTEND_DIST_DIR / "assets").is_dir():
    app.mount(
        "/assets",
        StaticFiles(directory=FRONTEND_DIST_DIR / "assets"),
        name="frontend-assets",
    )


@app.get("/{full_path:path}", include_in_schema=False)
def serve_spa_fallback(full_path: str):
    """Serve built React SPA in single-server production mode if `frontend/dist` exists."""
    if full_path.startswith(("api/", "media/")) or full_path in {"api", "media"}:
        raise HTTPException(status_code=404, detail="Not Found")

    index_file = FRONTEND_DIST_DIR / "index.html"
    if not index_file.is_file():
        raise HTTPException(status_code=404, detail="Not Found")

    if full_path:
        candidate = (FRONTEND_DIST_DIR / full_path).resolve()
        if FRONTEND_DIST_DIR.resolve() in candidate.parents and candidate.is_file():
            return FileResponse(candidate)

    return FileResponse(index_file)
