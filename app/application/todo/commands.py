from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CreateTodoCommand:
    title: str
    user_id: int
    description: Optional[str] = None
    priority: int = 1


@dataclass(frozen=True)
class UpdateTodoCommand:
    todo_id: int
    user_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[int] = None


@dataclass(frozen=True)
class DeleteTodoCommand:
    todo_id: int
    user_id: int
