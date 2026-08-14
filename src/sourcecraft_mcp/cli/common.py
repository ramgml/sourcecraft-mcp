"""Shared helpers for the SourceCraft CLI."""

from __future__ import annotations

import asyncio
import json
import os
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, TypeVar

import typer
from pydantic import BaseModel
from pysourcecraft import SourceCraftClient
from rich.console import Console
from rich.table import Table

console = Console()
err_console = Console(stderr=True)

T = TypeVar("T")

DEFAULT_BASE_URL = "https://api.sourcecraft.tech"


@dataclass
class CliContext:
    """Global CLI options shared by all commands."""

    token: str | None
    base_url: str
    as_json: bool


def get_cli_context(ctx: typer.Context) -> CliContext:
    """Get the global CLI context from a typer context."""
    obj = ctx.find_root().obj
    assert isinstance(obj, CliContext)
    return obj


def create_client(cli_ctx: CliContext) -> SourceCraftClient:
    """Create a SourceCraft API client from CLI context."""
    token = cli_ctx.token or os.environ.get("SOURCECRAFT_API_TOKEN")
    if not token:
        err_console.print(
            "[red]Error:[/red] API token is required. "
            "Set SOURCECRAFT_API_TOKEN env var or pass --token."
        )
        raise typer.Exit(code=2)
    base_url = cli_ctx.base_url or os.environ.get("SOURCECRAFT_BASE_URL") or DEFAULT_BASE_URL
    return SourceCraftClient(api_token=token, base_url=base_url)


def run_command(
    ctx: typer.Context,
    handler: Callable[[SourceCraftClient], Awaitable[T]],
    render: Callable[[T], None] | None = None,
) -> None:
    """Run an async handler against the API and render the result.

    Args:
        ctx: Typer command context
        handler: Async function receiving the API client
        render: Function rendering the result in human-readable form
            (used when --json is not set). Defaults to JSON output.
    """
    cli_ctx = get_cli_context(ctx)
    client = create_client(cli_ctx)

    async def _run() -> T:
        try:
            return await handler(client)
        finally:
            await client.close()

    try:
        result = asyncio.run(_run())
    except typer.Exit:
        raise
    except Exception as e:
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from e

    if cli_ctx.as_json or render is None:
        console.print_json(json.dumps(to_jsonable(result), ensure_ascii=False))
    else:
        render(result)


def to_jsonable(value: Any) -> Any:
    """Convert pydantic models and containers to JSON-serializable structures."""
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json", exclude_none=True)
    if isinstance(value, (list, tuple)):
        return [to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {key: to_jsonable(item) for key, item in value.items()}
    return value


def render_table(title: str, columns: list[str], rows: list[list[Any]]) -> None:
    """Render rows as a rich table."""
    table = Table(title=title)
    for column in columns:
        table.add_column(column)
    for row in rows:
        table.add_row(*(str(cell) if cell is not None else "" for cell in row))
    console.print(table)


def render_fields(title: str, fields: list[tuple[str, Any]]) -> None:
    """Render a single object as key-value pairs."""
    table = Table(title=title, show_header=False)
    table.add_column("Field", style="bold")
    table.add_column("Value")
    for name, value in fields:
        if value is not None and value != "":
            table.add_row(name, str(value))
    console.print(table)


def split_repo(repo: str) -> tuple[str, str]:
    """Split an 'owner/repo' argument into owner and repo."""
    parts = repo.split("/")
    if len(parts) != 2 or not all(parts):
        err_console.print(
            f"[red]Error:[/red] expected repository in 'owner/repo' form, got '{repo}'"
        )
        raise typer.Exit(code=2)
    return parts[0], parts[1]


RepoArg = typer.Argument(..., help="Repository in 'owner/repo' form.", metavar="OWNER/REPO")
