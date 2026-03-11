from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate


class TodoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, todo_id: int) -> Optional[Todo]:
        result = await self.db.execute(select(Todo).where(Todo.id == todo_id))
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Todo]:
        result = await self.db.execute(
            select(Todo)
            .where(Todo.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Todo.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, todo: TodoCreate, user_id: int) -> Todo:
        db_todo = Todo(**todo.model_dump(), user_id=user_id)
        self.db.add(db_todo)
        await self.db.flush()
        await self.db.refresh(db_todo)
        return db_todo

    async def update(self, todo_id: int, todo_update: TodoUpdate) -> Optional[Todo]:
        db_todo = await self.get_by_id(todo_id)
        if not db_todo:
            return None
        update_data = todo_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_todo, field, value)
        await self.db.flush()
        await self.db.refresh(db_todo)
        return db_todo

    async def delete(self, todo_id: int) -> bool:
        db_todo = await self.get_by_id(todo_id)
        if not db_todo:
            return False
        await self.db.delete(db_todo)
        return True
