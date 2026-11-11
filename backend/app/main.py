"""FastAPI entry point: serves the JSON API under /api and the compiled SPA at /."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.app.config import PROJECT_ROOT

FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"

app = FastAPI(title="ExTrack", version="0.1.0")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# The compiled frontend is served by the backend, so a single process is enough.
# Mounted last so it never shadows /api routes.
if FRONTEND_DIST.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
