from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.domain.todo.entity import Todo
from app.domain.todo.value_objects import Priority
from app.domain.todo.repository import ITodoRepository
from app.domain.todo.exceptions import TodoNotFoundError
from app.infrastructure.persistence.models.todo import TodoORM


class SqlAlchemyTodoRepository(ITodoRepository):
    """SQLAlchemy implementation of ITodoRepository."""

    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_by_id(self, todo_id: int) -> Optional[Todo]:
        result = await self._db.execute(select(TodoORM).where(TodoORM.id == todo_id))
        orm = result.scalar_one_or_none()
        return self._to_entity(orm) if orm else None

    async def get_by_user(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Todo]:
        result = await self._db.execute(
            select(TodoORM)
            .where(TodoORM.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(TodoORM.created_at.desc())
        )
        return [self._to_entity(row) for row in result.scalars().all()]

    async def save(self, todo: Todo) -> Todo:
        if todo.id is None:
            orm = TodoORM(
                title=todo.title,
                description=todo.description,
                completed=todo.completed,
                priority=int(todo.priority),
                user_id=todo.user_id,
            )
            self._db.add(orm)
        else:
            result = await self._db.execute(select(TodoORM).where(TodoORM.id == todo.id))
            orm = result.scalar_one_or_none()
            if not orm:
                raise TodoNotFoundError(todo.id)
            orm.title = todo.title
            orm.description = todo.description
            orm.completed = todo.completed
            orm.priority = int(todo.priority)

        await self._db.flush()
        await self._db.refresh(orm)
        return self._to_entity(orm)

    async def delete(self, todo_id: int) -> bool:
        result = await self._db.execute(select(TodoORM).where(TodoORM.id == todo_id))
        orm = result.scalar_one_or_none()
        if not orm:
            return False
        await self._db.delete(orm)
        await self._db.flush()
        return True

    @staticmethod
    def _to_entity(orm: TodoORM) -> Todo:
        return Todo(
            id=orm.id,
            title=orm.title,
            description=orm.description,
            completed=orm.completed,
            priority=Priority(orm.priority),
            user_id=orm.user_id,
            created_at=orm.created_at,
        )
