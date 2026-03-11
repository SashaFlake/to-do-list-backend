from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.infrastructure.persistence.unit_of_work import UnitOfWork
from app.application.todo.use_cases import TodoUseCases
from app.application.todo.commands import (
    CreateTodoCommand,
    UpdateTodoCommand,
    DeleteTodoCommand,
)
from app.application.todo.queries import GetTodoQuery, ListTodosQuery
from app.api.v1.schemas.todo import (
    TodoCreateRequest,
    TodoUpdateRequest,
    TodoResponse,
)

router = APIRouter()


def get_use_cases(db: AsyncSession = Depends(get_db)) -> TodoUseCases:
    uow = UnitOfWork(db)
    return TodoUseCases(repository=uow.todos)


@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    body: TodoCreateRequest,
    use_cases: TodoUseCases = Depends(get_use_cases),
    db: AsyncSession = Depends(get_db),
):
    # TODO: replace stub with Depends(get_current_user) after Keycloak
    user_id = 1
    cmd = CreateTodoCommand(
        title=body.title,
        description=body.description,
        priority=body.priority,
        user_id=user_id,
    )
    async with UnitOfWork(db) as uow:
        uc = TodoUseCases(repository=uow.todos)
        dto = await uc.create(cmd)
    return TodoResponse.model_validate(dto.__dict__)


@router.get("/", response_model=List[TodoResponse])
async def list_todos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    user_id = 1  # TODO: Keycloak
    async with UnitOfWork(db) as uow:
        uc = TodoUseCases(repository=uow.todos)
        dtos = await uc.list(ListTodosQuery(user_id=user_id, skip=skip, limit=limit))
    return [TodoResponse.model_validate(d.__dict__) for d in dtos]


@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
):
    user_id = 1  # TODO: Keycloak
    async with UnitOfWork(db) as uow:
        uc = TodoUseCases(repository=uow.todos)
        dto = await uc.get(GetTodoQuery(todo_id=todo_id, user_id=user_id))
    if not dto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return TodoResponse.model_validate(dto.__dict__)


@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: int,
    body: TodoUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    user_id = 1  # TODO: Keycloak
    cmd = UpdateTodoCommand(
        todo_id=todo_id,
        user_id=user_id,
        title=body.title,
        description=body.description,
        completed=body.completed,
        priority=body.priority,
    )
    async with UnitOfWork(db) as uow:
        uc = TodoUseCases(repository=uow.todos)
        dto = await uc.update(cmd)
    if not dto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return TodoResponse.model_validate(dto.__dict__)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
):
    user_id = 1  # TODO: Keycloak
    cmd = DeleteTodoCommand(todo_id=todo_id, user_id=user_id)
    async with UnitOfWork(db) as uow:
        uc = TodoUseCases(repository=uow.todos)
        if not await uc.delete(cmd):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
