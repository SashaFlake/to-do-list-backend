class TodoNotFoundError(Exception):
    """Raised when a Todo aggregate is not found by id."""

    def __init__(self, todo_id: int) -> None:
        self.todo_id = todo_id
        super().__init__(f"Todo with id={todo_id} not found")


class TodoAccessDeniedError(Exception):
    """Raised when a user tries to access a Todo they do not own."""

    def __init__(self, todo_id: int, user_id: str) -> None:
        self.todo_id = todo_id
        self.user_id = user_id
        super().__init__(f"User {user_id} does not have access to Todo {todo_id}")
