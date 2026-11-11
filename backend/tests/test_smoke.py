from fastapi.testclient import TestClient

from backend.app.config import Settings, load_source_config
from backend.app.main import app


def test_health() -> None:
    response = TestClient(app).get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_defaults_bind_localhost(monkeypatch) -> None:
    monkeypatch.delenv("LISTEN_LAN", raising=False)
    settings = Settings(_env_file=None)
    assert settings.host == "127.0.0.1"
    assert settings.database_path.is_absolute()


def test_source_config_loads() -> None:
    config = load_source_config(Settings(_env_file=None).config_path)
    sections = [s["name"] for s in config["excel"]["sections"]]
    assert sections == ["Spesa", "Affitto", "Abbonamenti", "Varie"]
