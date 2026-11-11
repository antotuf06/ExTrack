#!/usr/bin/env sh
# ExTrack launcher for Linux/macOS (portability; the main target is start.bat).
set -eu
cd "$(dirname "$0")"

command -v uv >/dev/null 2>&1 || { echo "[ExTrack] uv not found: https://docs.astral.sh/uv/"; exit 1; }

if [ ! -f data/.env ]; then
    echo "[ExTrack] data/.env not found: creating it from .env.example."
    mkdir -p data
    cp .env.example data/.env
fi

[ -f frontend/dist/index.html ] || echo "[ExTrack] Frontend not built: run 'npm install && npm run build' in frontend/."

uv sync --no-dev
uv run --no-dev alembic upgrade head
exec uv run --no-dev python -m backend.app
