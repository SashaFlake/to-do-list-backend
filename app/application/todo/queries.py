from dataclasses import dataclass


@dataclass(frozen=True)
class GetTodoQuery:
    todo_id: int
    user_id: int


@dataclass(frozen=True)
class ListTodosQuery:
    user_id: int
    skip: int = 0
    limit: int = 100
