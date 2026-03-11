import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.unit_of_work import IUnitOfWork
from app.infrastructure.persistence.repositories.todo_repository import SqlAlchemyTodoRepository

logger = logging.getLogger(__name__)


class UnitOfWork(IUnitOfWork):
    """
    SQLAlchemy implementation of IUnitOfWork.
    Controls transaction boundary and dispatches domain events after commit.
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
            await self._dispatch_events()

    async def _dispatch_events(self) -> None:
        """Collect and dispatch domain events from all tracked aggregates.

        TODO: replace logger with a real async message bus (e.g. Redis Streams,
        RabbitMQ) once the infrastructure is available.
        """
        for aggregate in self.todos._tracked:
            for event in aggregate.pull_events():
                logger.info("[DomainEvent] %s", event)
