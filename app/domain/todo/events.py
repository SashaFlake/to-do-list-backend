from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TodoCreated:
    todo_id: int
    user_id: int
    title: str
    occurred_at: datetime


@dataclass(frozen=True)
class TodoCompleted:
    todo_id: int
    user_id: int
    occurred_at: datetime


@dataclass(frozen=True)
class TodoDeleted:
    todo_id: int
    user_id: int
    occurred_at: datetime
