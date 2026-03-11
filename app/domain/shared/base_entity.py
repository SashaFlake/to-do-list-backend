from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class BaseEntity:
    """Shared kernel base for all aggregate roots."""
    id: Optional[int] = field(default=None)
    _events: List[Any] = field(default_factory=list, init=False, repr=False, compare=False)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def push_event(self, event: Any) -> None:
        """Register a domain event to be dispatched after commit."""
        self._events.append(event)

    def pull_events(self) -> List[Any]:
        """Return and clear collected domain events."""
        events, self._events = self._events, []
        return events
