from typing import List, Optional
from datetime import datetime, timezone

from app.domain.todo.entity import Todo
from app.domain.todo.value_objects import Priority
from app.domain.todo.repository import ITodoRepository
from app.domain.todo.events import TodoCreated, TodoCompleted, TodoDeleted
from app.application.todo.commands import (
    CreateTodoCommand,
    UpdateTodoCommand,
    DeleteTodoCommand,
)
from app.application.todo.queries import GetTodoQuery, ListTodosQuery
from app.application.todo.dto import TodoDTO


class TodoUseCases:
    """Application service — orchestrates domain logic."""

    def __init__(self, repository: ITodoRepository):
        self._repo = repository

    # --- Commands ---

    async def create(self, cmd: CreateTodoCommand) -> TodoDTO:
        todo = Todo(
            id=None,
            title=cmd.title,
            description=cmd.description,
            completed=False,
            priority=Priority.from_int(cmd.priority),
            user_id=cmd.user_id,
        )
        saved = await self._repo.save(todo)
        saved.push_event(
            TodoCreated(
                todo_id=saved.id,
                user_id=saved.user_id,
                title=saved.title,
                occurred_at=datetime.now(timezone.utc),
            )
        )
        return self._to_dto(saved)

    async def update(self, cmd: UpdateTodoCommand) -> Optional[TodoDTO]:
        todo = await self._repo.get_by_id(cmd.todo_id)
        if not todo or todo.user_id != cmd.user_id:
            return None

        if cmd.title is not None:
            todo.update_title(cmd.title)
        if cmd.description is not None:
            todo.update_description(cmd.description)
        if cmd.completed is True:
            todo.complete()
            todo.push_event(
                TodoCompleted(
                    todo_id=todo.id,
                    user_id=todo.user_id,
                    occurred_at=datetime.now(timezone.utc),
                )
            )
        elif cmd.completed is False:
            todo.uncomplete()
        if cmd.priority is not None:
            todo.change_priority(Priority.from_int(cmd.priority))

        saved = await self._repo.save(todo)
        return self._to_dto(saved)

    async def delete(self, cmd: DeleteTodoCommand) -> bool:
        todo = await self._repo.get_by_id(cmd.todo_id)
        if not todo or todo.user_id != cmd.user_id:
            return False
        result = await self._repo.delete(cmd.todo_id)
        if result:
            todo.push_event(
                TodoDeleted(
                    todo_id=cmd.todo_id,
                    user_id=cmd.user_id,
                    occurred_at=datetime.now(timezone.utc),
                )
            )
        return result

    # --- Queries ---

    async def get(self, query: GetTodoQuery) -> Optional[TodoDTO]:
        todo = await self._repo.get_by_id(query.todo_id)
        if not todo or todo.user_id != query.user_id:
            return None
        return self._to_dto(todo)

    async def list(self, query: ListTodosQuery) -> List[TodoDTO]:
        todos = await self._repo.get_by_user(
            query.user_id, skip=query.skip, limit=query.limit
        )
        return [self._to_dto(t) for t in todos]

    # --- Mapper ---

    @staticmethod
    def _to_dto(todo: Todo) -> TodoDTO:
        return TodoDTO(
            id=todo.id,
            title=todo.title,
            description=todo.description,
            completed=todo.completed,
            priority=int(todo.priority),
            user_id=todo.user_id,
            created_at=todo.created_at,
        )
