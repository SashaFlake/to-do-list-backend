from abc import ABC, abstractmethod

from app.domain.todo.repository import ITodoRepository


class IUnitOfWork(ABC):
    """
    Port: application layer contract for transaction boundary.
    Infrastructure provides the concrete implementation.
    """

    todos: ITodoRepository

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...

    async def __aenter__(self) -> "IUnitOfWork":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
