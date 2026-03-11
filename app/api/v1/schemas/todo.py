from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TodoCreateRequest(BaseModel):
    """HTTP request schema — API layer only."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    priority: int = Field(1, ge=1, le=5)


class TodoUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=1, le=5)


class TodoResponse(BaseModel):
    """HTTP response schema — API layer only."""
    id: int
    title: str
    description: Optional[str]
    completed: bool
    priority: int
    user_id: int
    created_at: Optional[datetime]

    class Config:
        from_attributes = True
