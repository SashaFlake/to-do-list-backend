from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.repositories.todo import TodoRepository
from app.schemas.todo import TodoCreate, TodoUpdate, TodoResponse
from app.core.cache import CacheService


class TodoService:
    def __init__(self, db: AsyncSession):
        self.repository = TodoRepository(db)
        self.cache = CacheService()

    async def create_todo(self, todo: TodoCreate, user_id: int) -> TodoResponse:
        db_todo = await self.repository.create(todo, user_id)
        await self.repository.db.commit()
        await self.cache.delete(f"user_todos:{user_id}")
        return TodoResponse.model_validate(db_todo)

    async def get_todo(self, todo_id: int) -> Optional[TodoResponse]:
        cache_key = f"todo:{todo_id}"
        cached = await self.cache.get(cache_key)
        if cached:
            return TodoResponse(**cached)

        db_todo = await self.repository.get_by_id(todo_id)
        if db_todo:
            response = TodoResponse.model_validate(db_todo)
            await self.cache.set(cache_key, response.model_dump(mode="json"))
            return response
        return None

    async def get_todos(self, user_id: int, skip: int = 0, limit: int = 100) -> List[TodoResponse]:
        cache_key = f"user_todos:{user_id}:{skip}:{limit}"
        cached = await self.cache.get(cache_key)
        if cached:
            return [TodoResponse(**item) for item in cached]

        todos = await self.repository.get_by_user(user_id, skip, limit)
        responses = [TodoResponse.model_validate(t) for t in todos]
        await self.cache.set(cache_key, [r.model_dump(mode="json") for r in responses])
        return responses

    async def update_todo(self, todo_id: int, todo_update: TodoUpdate) -> Optional[TodoResponse]:
        db_todo = await self.repository.update(todo_id, todo_update)
        if db_todo:
            await self.repository.db.commit()
            await self.cache.delete(f"todo:{todo_id}")
            await self.cache.delete(f"user_todos:{db_todo.user_id}")
            return TodoResponse.model_validate(db_todo)
        return None

    async def delete_todo(self, todo_id: int) -> bool:
        db_todo = await self.repository.get_by_id(todo_id)
        if not db_todo:
            return False
        user_id = db_todo.user_id
        result = await self.repository.delete(todo_id)
        if result:
            await self.repository.db.commit()
            await self.cache.delete(f"todo:{todo_id}")
            await self.cache.delete(f"user_todos:{user_id}")
        return result
