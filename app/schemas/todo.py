from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TodoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    priority: int = Field(1, ge=1, le=5)


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=1, le=5)


class TodoResponse(TodoBase):
    id: int
    completed: bool
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True
