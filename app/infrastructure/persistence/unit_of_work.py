from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.persistence.repositories.todo_repository import SqlAlchemyTodoRepository


class UnitOfWork:
    """
    Unit of Work pattern — controls transaction boundary.
    Use cases commit via UoW, not via repository directly.
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
