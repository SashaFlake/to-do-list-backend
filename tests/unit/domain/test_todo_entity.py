"""Unit tests for Todo aggregate root — pure domain logic, zero dependencies."""
import pytest
from app.domain.todo.entity import Todo
from app.domain.todo.value_objects import Priority


def make_todo(**kwargs) -> Todo:
    defaults = dict(
        id=1,
        title="Buy milk",
        description=None,
        completed=False,
        priority=Priority.NORMAL,
        user_id="123",
    )
    return Todo(**{**defaults, **kwargs})


# --- complete / uncomplete ---

def test_should_mark_completed_when_complete_called():
    todo = make_todo(completed=False)
    todo.complete()
    assert todo.completed is True


def test_should_mark_not_completed_when_uncomplete_called():
    todo = make_todo(completed=True)
    todo.uncomplete()
    assert todo.completed is False


def test_should_remain_completed_when_complete_called_twice():
    todo = make_todo(completed=False)
    todo.complete()
    todo.complete()
    assert todo.completed is True


# --- update_title ---

def test_should_update_title_when_valid_string_given():
    todo = make_todo(title="Old title")
    todo.update_title("New title")
    assert todo.title == "New title"


def test_should_strip_whitespace_when_title_has_leading_spaces():
    todo = make_todo()
    todo.update_title("  trimmed  ")
    assert todo.title == "trimmed"


def test_should_raise_when_title_is_empty_string():
    todo = make_todo()
    with pytest.raises(ValueError, match="Title cannot be empty"):
        todo.update_title("")


def test_should_raise_when_title_is_only_whitespace():
    todo = make_todo()
    with pytest.raises(ValueError, match="Title cannot be empty"):
        todo.update_title("   ")


# --- update_description ---

def test_should_update_description_when_string_given():
    todo = make_todo(description=None)
    todo.update_description("Some details")
    assert todo.description == "Some details"


def test_should_clear_description_when_none_given():
    todo = make_todo(description="existing")
    todo.update_description(None)
    assert todo.description is None


# --- change_priority ---

def test_should_change_priority_when_valid_priority_given():
    todo = make_todo(priority=Priority.LOW)
    todo.change_priority(Priority.CRITICAL)
    assert todo.priority == Priority.CRITICAL


# --- Priority value object ---

def test_should_create_priority_when_valid_int_given():
    assert Priority.from_int(1) == Priority.LOW
    assert Priority.from_int(5) == Priority.CRITICAL


def test_should_raise_when_priority_out_of_range():
    with pytest.raises(ValueError, match="Priority must be between 1 and 5"):
        Priority.from_int(0)

    with pytest.raises(ValueError, match="Priority must be between 1 and 5"):
        Priority.from_int(6)


# --- id comparison ---

def test_should_be_equal_when_same_id():
    a = make_todo(id=1)
    b = make_todo(id=1, title="Different title")
    assert a.id == b.id


def test_should_not_be_equal_when_different_id():
    a = make_todo(id=1)
    b = make_todo(id=2)
    assert a.id != b.id
