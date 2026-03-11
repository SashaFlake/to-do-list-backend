"""Unit tests for TodoUseCases — application layer with mock repository."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone

from app.domain.todo.entity import Todo
from app.domain.todo.value_objects import Priority
from app.application.todo.use_cases import TodoUseCases
from app.application.todo.commands import (
    CreateTodoCommand,
    UpdateTodoCommand,
    DeleteTodoCommand,
)
from app.application.todo.queries import GetTodoQuery, ListTodosQuery


def make_todo(**kwargs) -> Todo:
    defaults = dict(
        id=1,
        title="Buy milk",
        description=None,
        completed=False,
        priority=Priority.NORMAL,
        user_id=42,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    return Todo(**{**defaults, **kwargs})


def make_repo(**kwargs) -> AsyncMock:
    """Returns mock ITodoRepository with sensible defaults."""
    repo = AsyncMock()
    repo.save = AsyncMock(side_effect=lambda todo: todo)
    repo.get_by_id = AsyncMock(return_value=None)
    repo.get_by_user = AsyncMock(return_value=[])
    repo.delete = AsyncMock(return_value=True)
    for k, v in kwargs.items():
        setattr(repo, k, v)
    return repo


# --- create ---

@pytest.mark.asyncio
async def test_should_return_dto_when_todo_created():
    saved = make_todo(id=1)
    repo = make_repo(save=AsyncMock(return_value=saved))
    uc = TodoUseCases(repo)

    cmd = CreateTodoCommand(title="Buy milk", user_id=42, priority=3)
    dto = await uc.create(cmd)

    assert dto.id == 1
    assert dto.title == "Buy milk"
    assert dto.completed is False
    assert dto.user_id == 42


@pytest.mark.asyncio
async def test_should_call_repo_save_when_todo_created():
    repo = make_repo(save=AsyncMock(return_value=make_todo()))
    uc = TodoUseCases(repo)

    await uc.create(CreateTodoCommand(title="Test", user_id=1, priority=1))

    repo.save.assert_called_once()
    saved_entity = repo.save.call_args[0][0]
    assert saved_entity.id is None  # new entity before persistence
    assert saved_entity.completed is False


@pytest.mark.asyncio
async def test_should_set_priority_when_create_command_has_priority():
    saved = make_todo(priority=Priority.HIGH)
    repo = make_repo(save=AsyncMock(return_value=saved))
    uc = TodoUseCases(repo)

    dto = await uc.create(CreateTodoCommand(title="Urgent", user_id=1, priority=4))

    assert dto.priority == 4


# --- update ---

@pytest.mark.asyncio
async def test_should_return_updated_dto_when_title_changed():
    existing = make_todo(title="Old")
    updated = make_todo(title="New")
    repo = make_repo(
        get_by_id=AsyncMock(return_value=existing),
        save=AsyncMock(return_value=updated),
    )
    uc = TodoUseCases(repo)

    dto = await uc.update(UpdateTodoCommand(todo_id=1, user_id=42, title="New"))

    assert dto.title == "New"


@pytest.mark.asyncio
async def test_should_return_none_when_todo_not_found_on_update():
    repo = make_repo(get_by_id=AsyncMock(return_value=None))
    uc = TodoUseCases(repo)

    dto = await uc.update(UpdateTodoCommand(todo_id=999, user_id=42))

    assert dto is None


@pytest.mark.asyncio
async def test_should_return_none_when_user_does_not_own_todo_on_update():
    other_users_todo = make_todo(user_id=99)
    repo = make_repo(get_by_id=AsyncMock(return_value=other_users_todo))
    uc = TodoUseCases(repo)

    dto = await uc.update(UpdateTodoCommand(todo_id=1, user_id=42, title="Hack"))

    assert dto is None
    repo.save.assert_not_called()


@pytest.mark.asyncio
async def test_should_mark_completed_when_update_command_sets_completed_true():
    existing = make_todo(completed=False)
    repo = make_repo(
        get_by_id=AsyncMock(return_value=existing),
        save=AsyncMock(side_effect=lambda t: t),
    )
    uc = TodoUseCases(repo)

    dto = await uc.update(UpdateTodoCommand(todo_id=1, user_id=42, completed=True))

    assert dto.completed is True


@pytest.mark.asyncio
async def test_should_unmark_completed_when_update_command_sets_completed_false():
    existing = make_todo(completed=True)
    repo = make_repo(
        get_by_id=AsyncMock(return_value=existing),
        save=AsyncMock(side_effect=lambda t: t),
    )
    uc = TodoUseCases(repo)

    dto = await uc.update(UpdateTodoCommand(todo_id=1, user_id=42, completed=False))

    assert dto.completed is False


@pytest.mark.asyncio
async def test_should_not_change_title_when_update_command_title_is_none():
    existing = make_todo(title="Keep this")
    repo = make_repo(
        get_by_id=AsyncMock(return_value=existing),
        save=AsyncMock(side_effect=lambda t: t),
    )
    uc = TodoUseCases(repo)

    dto = await uc.update(UpdateTodoCommand(todo_id=1, user_id=42, title=None))

    assert dto.title == "Keep this"


# --- delete ---

@pytest.mark.asyncio
async def test_should_return_true_when_todo_deleted():
    repo = make_repo(
        get_by_id=AsyncMock(return_value=make_todo()),
        delete=AsyncMock(return_value=True),
    )
    uc = TodoUseCases(repo)

    result = await uc.delete(DeleteTodoCommand(todo_id=1, user_id=42))

    assert result is True
    repo.delete.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_should_return_false_when_todo_not_found_on_delete():
    repo = make_repo(get_by_id=AsyncMock(return_value=None))
    uc = TodoUseCases(repo)

    result = await uc.delete(DeleteTodoCommand(todo_id=999, user_id=42))

    assert result is False
    repo.delete.assert_not_called()


@pytest.mark.asyncio
async def test_should_return_false_when_user_does_not_own_todo_on_delete():
    other_users_todo = make_todo(user_id=99)
    repo = make_repo(get_by_id=AsyncMock(return_value=other_users_todo))
    uc = TodoUseCases(repo)

    result = await uc.delete(DeleteTodoCommand(todo_id=1, user_id=42))

    assert result is False
    repo.delete.assert_not_called()


# --- get ---

@pytest.mark.asyncio
async def test_should_return_dto_when_todo_found_and_owned():
    repo = make_repo(get_by_id=AsyncMock(return_value=make_todo(user_id=42)))
    uc = TodoUseCases(repo)

    dto = await uc.get(GetTodoQuery(todo_id=1, user_id=42))

    assert dto is not None
    assert dto.id == 1


@pytest.mark.asyncio
async def test_should_return_none_when_todo_not_found_on_get():
    repo = make_repo(get_by_id=AsyncMock(return_value=None))
    uc = TodoUseCases(repo)

    dto = await uc.get(GetTodoQuery(todo_id=999, user_id=42))

    assert dto is None


@pytest.mark.asyncio
async def test_should_return_none_when_user_does_not_own_todo_on_get():
    repo = make_repo(get_by_id=AsyncMock(return_value=make_todo(user_id=99)))
    uc = TodoUseCases(repo)

    dto = await uc.get(GetTodoQuery(todo_id=1, user_id=42))

    assert dto is None


# --- list ---

@pytest.mark.asyncio
async def test_should_return_empty_list_when_user_has_no_todos():
    repo = make_repo(get_by_user=AsyncMock(return_value=[]))
    uc = TodoUseCases(repo)

    dtos = await uc.list(ListTodosQuery(user_id=42))

    assert dtos == []


@pytest.mark.asyncio
async def test_should_return_list_of_dtos_when_user_has_todos():
    todos = [make_todo(id=1), make_todo(id=2), make_todo(id=3)]
    repo = make_repo(get_by_user=AsyncMock(return_value=todos))
    uc = TodoUseCases(repo)

    dtos = await uc.list(ListTodosQuery(user_id=42))

    assert len(dtos) == 3
    assert [d.id for d in dtos] == [1, 2, 3]


@pytest.mark.asyncio
async def test_should_pass_pagination_to_repo_when_list_called_with_skip_and_limit():
    repo = make_repo(get_by_user=AsyncMock(return_value=[]))
    uc = TodoUseCases(repo)

    await uc.list(ListTodosQuery(user_id=42, skip=10, limit=5))

    repo.get_by_user.assert_called_once_with(42, skip=10, limit=5)
