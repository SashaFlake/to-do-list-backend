from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api.v1.dependencies import get_current_user
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
from todo_auth import TokenPayload

router = APIRouter()


@router.post(
    "/",
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать задачу",
    description="Создаёт новую задачу для текущего пользователя. `completed` автоматически `false`.",
)
async def create_todo(
    body: TodoCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    user_id = current_user.sub
    cmd = CreateTodoCommand(
        title=body.title,
        description=body.description,
        priority=body.priority,
        user_id=user_id,
    )
    async with UnitOfWork(db) as uow:
        dto = await TodoUseCases(uow.todos).create(cmd)
    return TodoResponse.model_validate(dto.__dict__)


@router.get(
    "/",
    response_model=List[TodoResponse],
    summary="Список задач",
    description="Возвращает все задачи текущего пользователя с поддержкой пагинации через `skip` / `limit`.",
)
async def list_todos(
    skip: int = Query(0, ge=0, description="Пропустить N задач с начала"),
    limit: int = Query(100, ge=1, le=1000, description="Максимальное количество задач в ответе"),
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    user_id = current_user.sub
    async with UnitOfWork(db) as uow:
        dtos = await TodoUseCases(uow.todos).list(
            ListTodosQuery(user_id=user_id, skip=skip, limit=limit)
        )
    return [TodoResponse.model_validate(d.__dict__) for d in dtos]


@router.get(
    "/{todo_id}",
    response_model=TodoResponse,
    summary="Получить задачу",
    description="Возвращает задачу по `todo_id`. Доступна только владельцу.",
    responses={404: {"description": "Задача не найдена"}},
)
async def get_todo(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    user_id = current_user.sub
    async with UnitOfWork(db) as uow:
        dto = await TodoUseCases(uow.todos).get(
            GetTodoQuery(todo_id=todo_id, user_id=user_id)
        )
    if not dto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return TodoResponse.model_validate(dto.__dict__)


@router.put(
    "/{todo_id}",
    response_model=TodoResponse,
    summary="Обновить задачу",
    description=(
        "Частичное обновление задачи. Передавайте только те поля, которые нужно изменить.\n\n"
        "Для пометки задачи выполненной: `{\"completed\": true}`"
    ),
    responses={404: {"description": "Задача не найдена"}},
)
async def update_todo(
    todo_id: int,
    body: TodoUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    user_id = current_user.sub
    cmd = UpdateTodoCommand(
        todo_id=todo_id,
        user_id=user_id,
        title=body.title,
        description=body.description,
        completed=body.completed,
        priority=body.priority,
    )
    async with UnitOfWork(db) as uow:
        dto = await TodoUseCases(uow.todos).update(cmd)
    if not dto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return TodoResponse.model_validate(dto.__dict__)


@router.delete(
    "/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить задачу",
    description="Удаляет задачу по `todo_id`. Доступно только владельцу. Возвращает `204 No Content`.",
    responses={404: {"description": "Задача не найдена"}},
)
async def delete_todo(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    user_id = current_user.sub
    cmd = DeleteTodoCommand(todo_id=todo_id, user_id=user_id)
    async with UnitOfWork(db) as uow:
        if not await TodoUseCases(uow.todos).delete(cmd):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
