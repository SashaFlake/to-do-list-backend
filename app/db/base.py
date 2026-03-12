from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import all ORM models here so Alembic can detect them via target_metadata
from app.infrastructure.persistence.models.todo import TodoORM  # noqa: F401, E402
