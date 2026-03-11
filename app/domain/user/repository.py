from abc import ABC, abstractmethod
from typing import Optional
from app.domain.user.entity import User
from app.domain.user.value_objects import Email


class IUserRepository(ABC):
    """Abstract repository interface — domain doesn't know about DB."""

    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        ...

    @abstractmethod
    async def get_by_email(self, email: Email) -> Optional[User]:
        ...

    @abstractmethod
    async def save(self, user: User) -> User:
        """Create or update."""
        ...

    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        ...
