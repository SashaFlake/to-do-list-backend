from sqlalchemy import String, Integer, Boolean, ForeignKey, DateTime, func, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from typing import Optional
from app.db.session import Base


class TodoORM(Base, AsyncAttrs):
    """SQLAlchemy ORM model — infrastructure detail, not domain."""
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    priority: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    user_id: Mapped[str] = mapped_column(String(255), nullable=False)
