"""Tests for utility functions."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel

from sourcecraft_mcp.utils import format_datetime, format_error, format_list, format_model


class MockModel(BaseModel):
    """Mock Pydantic model for testing."""

    name: str
    value: int


class MockModelWithOptional(BaseModel):
    """Mock Pydantic model with optional fields."""

    name: str
    description: str | None = None


def test_format_model_with_valid_model() -> None:
    """Test formatting a valid Pydantic model."""
    model = MockModel(name="test", value=42)
    result = format_model(model)

    assert "test" in result
    assert "42" in result
    assert result.startswith("{")


def test_format_model_with_none() -> None:
    """Test formatting None returns 'No data'."""
    result = format_model(None)
    assert result == "No data"


def test_format_model_excludes_none() -> None:
    """Test that None values are excluded from output."""
    model = MockModelWithOptional(name="test")
    result = format_model(model)

    assert "test" in result
    # description is None and should be excluded
    assert "description" not in result


def test_format_list_with_empty_list() -> None:
    """Test formatting an empty list."""
    result = format_list([])
    assert result == "No items found"


def test_format_list_with_pydantic_models() -> None:
    """Test formatting a list of Pydantic models."""
    items = [MockModel(name="item1", value=1), MockModel(name="item2", value=2)]
    result = format_list(items)

    assert "item1" in result
    assert "item2" in result
    assert "- {" in result


def test_format_list_with_simple_items() -> None:
    """Test formatting a list of simple items."""
    items = ["item1", "item2", 123]
    result = format_list(items)

    assert "- item1" in result
    assert "- item2" in result
    assert "- 123" in result


def test_format_list_with_key_func() -> None:
    """Test formatting with a key function."""
    items = [MockModel(name="item1", value=1), MockModel(name="item2", value=2)]

    def get_name(item: MockModel) -> str:
        return item.name

    result = format_list(items, key_func=get_name)

    assert "- item1" in result
    assert "- item2" in result


def test_format_error_with_status_code() -> None:
    """Test formatting an error with status_code attribute."""

    class MockError(Exception):
        def __init__(self) -> None:
            super().__init__("Not found")
            self.status_code = 404

    error = MockError()
    result = format_error(error)

    assert "API Error (404): Not found" in result


def test_format_error_without_status_code() -> None:
    """Test formatting a regular exception."""
    error = ValueError("Something went wrong")
    result = format_error(error)

    assert "Error:" in result
    assert "Something went wrong" in result


def test_format_datetime_with_none() -> None:
    """Test formatting None datetime."""
    result = format_datetime(None)
    assert result == "N/A"


def test_format_datetime_with_datetime_object() -> None:
    """Test formatting a datetime object."""
    dt = datetime(2024, 1, 15, 10, 30, tzinfo=timezone.utc)
    result = format_datetime(dt)

    assert "2024-01-15" in result
    assert "10:30 UTC" in result


def test_format_datetime_with_iso_string() -> None:
    """Test formatting an ISO format string."""
    dt_str = "2024-01-15T10:30:00+00:00"
    result = format_datetime(dt_str)

    assert "2024-01-15" in result
    assert "10:30 UTC" in result


def test_format_datetime_with_z_suffix() -> None:
    """Test formatting an ISO string with Z suffix."""
    dt_str = "2024-01-15T10:30:00Z"
    result = format_datetime(dt_str)

    assert "2024-01-15" in result
    assert "10:30 UTC" in result


def test_format_datetime_with_invalid_string() -> None:
    """Test formatting an invalid datetime string."""
    dt_str = "not-a-datetime"
    result = format_datetime(dt_str)

    # Should return the original string if parsing fails
    assert result == "not-a-datetime"


def test_format_list_with_key_func_details() -> None:
    """Test formatting with key function includes additional details."""
    items = [MockModel(name="item1", value=1)]

    def get_name(item: MockModel) -> str:
        return item.name

    result = format_list(items, key_func=get_name)

    # Should show the key as header
    assert "- item1" in result
    # Should include other fields indented
    assert "  value:" in result


def test_format_list_with_empty_string_items() -> None:
    """Test formatting list with empty strings."""
    items = ["", "item"]
    result = format_list(items)

    assert "- " in result
    assert "- item" in result


def test_format_list_with_nested_models() -> None:
    """Test formatting list with nested model data."""

    class NestedModel(BaseModel):
        inner: MockModel

    items = [NestedModel(inner=MockModel(name="nested", value=99))]
    result = format_list(items)

    assert "nested" in result
