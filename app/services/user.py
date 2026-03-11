from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from typing import Optional

from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.cache import CacheService

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)
        self.cache = CacheService()

    def _hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    async def create_user(self, user: UserCreate) -> UserResponse:
        hashed_password = self._hash_password(user.password)
        db_user = await self.repository.create(user, hashed_password)
        return UserResponse.model_validate(db_user)

    async def get_user(self, user_id: int) -> Optional[UserResponse]:
        cache_key = f"user:{user_id}"
        cached = await self.cache.get(cache_key)
        if cached:
            return UserResponse(**cached)
        db_user = await self.repository.get_by_id(user_id)
        if db_user:
            user_response = UserResponse.model_validate(db_user)
            await self.cache.set(cache_key, user_response.model_dump(mode='json'))
            return user_response
        return None

    async def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[UserResponse]:
        # Fix: work with dict to avoid mutating the Pydantic schema object
        update_data = user_update.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = self._hash_password(update_data.pop("password"))
        db_user = await self.repository.update_by_data(user_id, update_data)
        if db_user:
            await self.cache.delete(f"user:{user_id}")
            return UserResponse.model_validate(db_user)
        return None

    async def delete_user(self, user_id: int) -> bool:
        result = await self.repository.delete(user_id)
        if result:
            await self.cache.delete(f"user:{user_id}")
        return result
