from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List

from app.models.user import User
from app.schemas.user import UserCreate


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        result = await self.db.execute(select(User).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, user: UserCreate, hashed_password: str) -> User:
        db_user = User(
            email=user.email,
            username=user.username,
            hashed_password=hashed_password,
        )
        self.db.add(db_user)
        await self.db.flush()
        await self.db.refresh(db_user)
        return db_user

    async def update_by_data(self, user_id: int, update_data: dict) -> Optional[User]:
        """Update user by pre-processed dict to allow password hashing outside schema."""
        db_user = await self.get_by_id(user_id)
        if not db_user:
            return None
        for field, value in update_data.items():
            setattr(db_user, field, value)
        await self.db.flush()
        await self.db.refresh(db_user)
        return db_user

    async def delete(self, user_id: int) -> bool:
        db_user = await self.get_by_id(user_id)
        if not db_user:
            return False
        await self.db.delete(db_user)
        return True
