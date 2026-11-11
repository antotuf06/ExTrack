"""SQLAlchemy models. Import every model module here so Alembic autogenerate sees it."""

from backend.app.models.base import Base

__all__ = ["Base"]
