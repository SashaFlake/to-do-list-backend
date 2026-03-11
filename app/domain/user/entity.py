from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from app.domain.user.value_objects import Email


@dataclass
class User:
    """User aggregate root."""
    id: Optional[int]
    email: Email
    username: str
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: Optional[datetime] = field(default=None)
    updated_at: Optional[datetime] = field(default=None)

    def deactivate(self) -> None:
        self.is_active = False

    def activate(self) -> None:
        self.is_active = True
