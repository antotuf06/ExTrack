"""Application settings, read from data/.env (secrets, paths) and config.yaml (layouts)."""

from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / "data" / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    data_dir: Path = Path("data")
    database_path: Path = Path("data/spese.sqlite")
    backup_dir: Path = Path("data/backups")
    backup_retention: int = 30
    config_path: Path = Path("config.yaml")

    port: int = 8000
    listen_lan: bool = False
    log_level: str = "INFO"

    cutoff_date: date = date(2026, 8, 1)
    account_holder_names: str = ""

    @field_validator("data_dir", "database_path", "backup_dir", "config_path")
    @classmethod
    def _resolve(cls, value: Path) -> Path:
        return value if value.is_absolute() else PROJECT_ROOT / value

    @property
    def host(self) -> str:
        return "0.0.0.0" if self.listen_lan else "127.0.0.1"

    @property
    def database_url(self) -> str:
        return f"sqlite:///{self.database_path.as_posix()}"

    @property
    def holder_names(self) -> list[str]:
        return [n.strip() for n in self.account_holder_names.split(",") if n.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


def load_source_config(path: Path | None = None) -> dict[str, Any]:
    """Load config.yaml (source layouts and bank profiles)."""
    path = path or get_settings().config_path
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}
