"""Production launcher used by start.bat / start.sh: `uv run python -m backend.app`."""

import sys

import uvicorn

from backend.app.config import get_settings


def main() -> None:
    settings = get_settings()
    if settings.listen_lan:
        # LAN access requires mandatory login (design §13), not implemented yet.
        sys.exit("LISTEN_LAN=true richiede il login, non ancora implementato. Avvio annullato.")
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    uvicorn.run(
        "backend.app.main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
