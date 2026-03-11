from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.session import get_db
from app.services.todo import TodoService
from app.schemas.todo import TodoCreate, TodoUpdate, TodoResponse

router = APIRouter()


def get_current_user_id() -> int:
    """
    Placeholder dependency - replace with Keycloak JWT validation.
    Should decode JWT token and return user.id from DB by keycloak sub.
    """
    # TODO: integrate with Keycloak
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Auth not implemented yet"
    )


@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo_in: TodoCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = TodoService(db)
    return await service.create_todo(todo_in, user_id)


@router.get("/", response_model=List[TodoResponse])
async def list_todos(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    completed: Optional[bool] = Query(None),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = TodoService(db)
    return await service.get_todos(user_id, skip, limit, completed)


@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(
    todo_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = TodoService(db)
    todo = await service.get_todo(todo_id, user_id)
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return todo


@router.patch("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: int,
    todo_update: TodoUpdate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = TodoService(db)
    todo = await service.update_todo(todo_id, user_id, todo_update)
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = TodoService(db)
    result = await service.delete_todo(todo_id, user_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
