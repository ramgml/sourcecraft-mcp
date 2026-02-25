"""Utility functions for SourceCraft MCP server."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel


def format_model(model: BaseModel | None) -> str:
    """Format a Pydantic model for display.

    Args:
        model: Pydantic model to format

    Returns:
        Formatted string representation
    """
    if model is None:
        return "No data"
    return json.dumps(model.model_dump(mode="json", exclude_none=True), indent=2)


def format_list(items: list[Any], key_func=None) -> str:
    """Format a list of items for display.

    Args:
        items: List of items to format
        key_func: Optional function to extract key from each item

    Returns:
        Formatted string representation
    """
    if not items:
        return "No items found"

    result = []
    for item in items:
        if isinstance(item, BaseModel):
            data = item.model_dump(mode="json", exclude_none=True)
            if key_func:
                key = key_func(item)
                result.append(f"- {key}")
                for k, v in data.items():
                    if k != key_func.__name__ if hasattr(key_func, "__name__") else True:
                        result.append(f"  {k}: {v}")
            else:
                result.append(f"- {data}")
        else:
            result.append(f"- {item}")

    return "\n".join(result)


def format_error(error: Exception) -> str:
    """Format an error for display.

    Args:
        error: Exception to format

    Returns:
        Formatted error message
    """
    if hasattr(error, "status_code"):
        return f"API Error ({error.status_code}): {error}"
    return f"Error: {error}"


def format_datetime(dt: datetime | str | None) -> str:
    """Format datetime for display.

    Args:
        dt: Datetime object or ISO string

    Returns:
        Formatted datetime string
    """
    if dt is None:
        return "N/A"
    if isinstance(dt, str):
        try:
            parsed_dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
            return parsed_dt.strftime("%Y-%m-%d %H:%M UTC")
        except ValueError:
            return dt
    return dt.strftime("%Y-%m-%d %H:%M UTC")
