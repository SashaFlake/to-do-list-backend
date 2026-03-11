from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from app.domain.todo.value_objects import Priority


@dataclass
class Todo:
    """Todo aggregate root."""
    id: Optional[int]
    title: str
    description: Optional[str]
    completed: bool
    priority: Priority
    user_id: int
    created_at: Optional[datetime] = field(default=None)

    def complete(self) -> None:
        """Mark todo as completed."""
        self.completed = True

    def uncomplete(self) -> None:
        """Mark todo as not completed."""
        self.completed = False

    def change_priority(self, priority: Priority) -> None:
        """Change priority of todo."""
        self.priority = priority

    def update_title(self, title: str) -> None:
        if not title or not title.strip():
            raise ValueError("Title cannot be empty")
        self.title = title.strip()

    def update_description(self, description: Optional[str]) -> None:
        self.description = description
