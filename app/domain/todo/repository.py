from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.todo.entity import Todo


class ITodoRepository(ABC):
    """Abstract repository interface — domain doesn't know about DB."""

    @abstractmethod
    async def get_by_id(self, todo_id: int) -> Optional[Todo]:
        ...

    @abstractmethod
    async def get_by_user(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Todo]:
        ...

    @abstractmethod
    async def save(self, todo: Todo) -> Todo:
        """Create or update."""
        ...

    @abstractmethod
    async def delete(self, todo_id: int) -> bool:
        ...
