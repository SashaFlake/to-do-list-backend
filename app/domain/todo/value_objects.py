from enum import IntEnum


class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    NORMAL = 3
    HIGH = 4
    CRITICAL = 5

    @classmethod
    def from_int(cls, value: int) -> "Priority":
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Priority must be between 1 and 5, got {value}")
