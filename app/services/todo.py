from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.repositories.todo import TodoRepository
from app.schemas.todo import TodoCreate, TodoUpdate, TodoResponse
from app.core.cache import CacheService


class TodoService:
    def __init__(self, db: AsyncSession):
        self.repository = TodoRepository(db)
        self.cache = CacheService()

    def _cache_key(self, todo_id: int, user_id: int) -> str:
        return f"todo:{user_id}:{todo_id}"

    def _list_cache_key(self, user_id: int) -> str:
        return f"todos:{user_id}"

    async def create_todo(self, todo_in: TodoCreate, user_id: int) -> TodoResponse:
        todo = await self.repository.create(todo_in, user_id)
        await self.cache.delete(self._list_cache_key(user_id))
        return TodoResponse.model_validate(todo)

    async def get_todo(self, todo_id: int, user_id: int) -> Optional[TodoResponse]:
        cache_key = self._cache_key(todo_id, user_id)
        cached = await self.cache.get(cache_key)
        if cached:
            return TodoResponse(**cached)
        todo = await self.repository.get_by_id(todo_id, user_id)
        if todo:
            response = TodoResponse.model_validate(todo)
            await self.cache.set(cache_key, response.model_dump(mode='json'))
            return response
        return None

    async def get_todos(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
        completed: Optional[bool] = None,
    ) -> List[TodoResponse]:
        todos = await self.repository.get_all_by_user(user_id, skip, limit, completed)
        return [TodoResponse.model_validate(t) for t in todos]

    async def update_todo(
        self, todo_id: int, user_id: int, todo_update: TodoUpdate
    ) -> Optional[TodoResponse]:
        todo = await self.repository.update(todo_id, user_id, todo_update)
        if todo:
            response = TodoResponse.model_validate(todo)
            await self.cache.delete(self._cache_key(todo_id, user_id))
            await self.cache.delete(self._list_cache_key(user_id))
            return response
        return None

    async def delete_todo(self, todo_id: int, user_id: int) -> bool:
        result = await self.repository.delete(todo_id, user_id)
        if result:
            await self.cache.delete(self._cache_key(todo_id, user_id))
            await self.cache.delete(self._list_cache_key(user_id))
        return result
