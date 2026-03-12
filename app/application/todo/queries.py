from dataclasses import dataclass


@dataclass(frozen=True)
class GetTodoQuery:
    todo_id: int
    user_id: str


@dataclass(frozen=True)
class ListTodosQuery:
    user_id: str
    skip: int = 0
    limit: int = 100
