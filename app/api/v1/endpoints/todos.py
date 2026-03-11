from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.services.todo import TodoService
from app.schemas.todo import TodoCreate, TodoUpdate, TodoResponse

router = APIRouter()


@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo: TodoCreate,
    db: AsyncSession = Depends(get_db)
):
    # TODO: replace with Depends(get_current_user) after Keycloak integration
    user_id = 1  # temporary stub
    service = TodoService(db)
    return await service.create_todo(todo, user_id)


@router.get("/", response_model=List[TodoResponse])
async def list_todos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    # TODO: replace with Depends(get_current_user) after Keycloak integration
    user_id = 1  # temporary stub
    service = TodoService(db)
    return await service.get_todos(user_id, skip, limit)


@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(
    todo_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = TodoService(db)
    todo = await service.get_todo(todo_id)
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return todo


@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: int,
    todo_update: TodoUpdate,
    db: AsyncSession = Depends(get_db)
):
    service = TodoService(db)
    todo = await service.update_todo(todo_id, todo_update)
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = TodoService(db)
    if not await service.delete_todo(todo_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
