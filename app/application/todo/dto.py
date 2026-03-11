from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class TodoDTO:
    """Data Transfer Object — crosses layer boundary."""
    id: int
    title: str
    description: Optional[str]
    completed: bool
    priority: int
    user_id: int
    created_at: Optional[datetime]
