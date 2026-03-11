from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List

from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate


class TodoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, todo_id: int, user_id: int) -> Optional[Todo]:
        result = await self.db.execute(
            select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_all_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
        completed: Optional[bool] = None,
    ) -> List[Todo]:
        query = select(Todo).where(Todo.user_id == user_id)
        if completed is not None:
            query = query.where(Todo.completed == completed)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, todo_in: TodoCreate, user_id: int) -> Todo:
        todo = Todo(**todo_in.model_dump(), user_id=user_id)
        self.db.add(todo)
        await self.db.flush()
        await self.db.refresh(todo)
        return todo

    async def update(self, todo_id: int, user_id: int, todo_update: TodoUpdate) -> Optional[Todo]:
        todo = await self.get_by_id(todo_id, user_id)
        if not todo:
            return None
        update_data = todo_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(todo, field, value)
        await self.db.flush()
        await self.db.refresh(todo)
        return todo

    async def delete(self, todo_id: int, user_id: int) -> bool:
        todo = await self.get_by_id(todo_id, user_id)
        if not todo:
            return False
        await self.db.delete(todo)
        return True
