from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BaseEntity:
    """Shared kernel base for all aggregate roots."""
    id: Optional[int] = field(default=None)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
