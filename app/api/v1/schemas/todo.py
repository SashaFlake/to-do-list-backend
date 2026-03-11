from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TodoCreateRequest(BaseModel):
    """Тело запроса для создания задачи."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Название задачи",
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Подробное описание задачи (необязательно)",
    )
    priority: int = Field(
        1,
        ge=1,
        le=5,
        description="Приоритет от 1 (низкий) до 5 (высокий)",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Купить продукты",
                    "description": "Молоко, хлеб, яйца",
                    "priority": 2,
                }
            ]
        }
    }


class TodoUpdateRequest(BaseModel):
    """Тело запроса для обновления задачи. Все поля опциональны."""

    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Новое название задачи",
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Новое описание",
    )
    completed: Optional[bool] = Field(
        None,
        description="true — пометить выполненной, false — снять отметку",
    )
    priority: Optional[int] = Field(
        None,
        ge=1,
        le=5,
        description="Новый приоритет (1–5)",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "completed": True,
                    "priority": 5,
                }
            ]
        }
    }


class TodoResponse(BaseModel):
    """Схема ответа задачи."""

    id: int = Field(..., description="Уникальный идентификатор задачи")
    title: str = Field(..., description="Название задачи")
    description: Optional[str] = Field(None, description="Описание задачи")
    completed: bool = Field(..., description="Признак выполнения")
    priority: int = Field(..., description="Приоритет (1–5)")
    user_id: int = Field(..., description="ID владельца задачи")
    created_at: Optional[datetime] = Field(None, description="Дата и время создания (UTC)")

    model_config = {"from_attributes": True}
