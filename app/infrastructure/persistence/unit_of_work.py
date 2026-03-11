from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.unit_of_work import IUnitOfWork
from app.infrastructure.persistence.repositories.todo_repository import SqlAlchemyTodoRepository


class UnitOfWork(IUnitOfWork):
    """
    SQLAlchemy implementation of IUnitOfWork.
    Controls transaction boundary: commit on success, rollback on error.
    """

    def __init__(self, db: AsyncSession):
        self._db = db
        self.todos = SqlAlchemyTodoRepository(db)

    async def commit(self) -> None:
        await self._db.commit()

    async def rollback(self) -> None:
        await self._db.rollback()

    async def __aenter__(self) -> "UnitOfWork":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
