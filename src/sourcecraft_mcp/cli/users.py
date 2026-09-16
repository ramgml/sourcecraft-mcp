"""User commands."""

from __future__ import annotations

import typer

from sourcecraft_mcp.cli.common import render_fields, render_table, run_command

app = typer.Typer(no_args_is_help=True)


def _render_user(u) -> None:
    render_fields(
        f"User @{u.username}",
        [
            ("Name", u.display_name),
            ("Bio", u.bio),
            (
                "Location",
                ", ".join(
                    part
                    for part in [
                        u.location.city if u.location else None,
                        u.location.country if u.location else None,
                    ]
                    if part
                )
                or None,
            ),
            ("Company", u.workplace.company if u.workplace else None),
            ("Position", u.workplace.position if u.workplace else None),
            ("Visibility", getattr(u, "visibility", None)),
        ],
    )


@app.command("me")
def current_user(ctx: typer.Context) -> None:
    """Информация о текущем пользователе."""

    async def handler(client):
        return await client.users.get_current()

    run_command(ctx, handler, _render_user)


@app.command("get")
def get_user(
    ctx: typer.Context, username: str = typer.Argument(..., help="Имя пользователя.")
) -> None:
    """Информация о пользователе."""

    async def handler(client):
        return await client.users.get(username=username)

    run_command(ctx, handler, _render_user)


@app.command("issues")
def my_issues(
    ctx: typer.Context,
    page_size: int = typer.Option(30, "--page-size"),
    page_token: str = typer.Option("", "--page-token"),
) -> None:
    """Мои issues."""

    async def handler(client):
        return await client.users.list_my_issues(page_size=page_size, page_token=page_token or None)

    def render(result):
        issues = getattr(result, "data", None) or []
        render_table(
            "My issues",
            ["#", "Title", "Status", "Priority"],
            [
                [
                    i.slug,
                    i.title,
                    i.status.name if i.status else "",
                    i.priority or "normal",
                ]
                for i in issues
            ],
        )

    run_command(ctx, handler, render)


@app.command("prs")
def user_prs(
    ctx: typer.Context,
    username: str = typer.Argument(..., help="Имя пользователя."),
    role: str = typer.Option("any", "--role", "-r", help="author | reviewer | any"),
    page_size: int = typer.Option(30, "--page-size"),
    page_token: str = typer.Option("", "--page-token"),
) -> None:
    """Pull requests пользователя."""

    async def handler(client):
        return await client.users.list_pull_requests(
            username=username, role=role, page_size=page_size, page_token=page_token or None
        )

    def render(result):
        prs = getattr(result, "data", None) or []
        render_table(
            f"PRs of @{username}",
            ["#", "Title", "Status", "Branch"],
            [[p.slug, p.title, p.status, f"{p.source_branch} → {p.target_branch}"] for p in prs],
        )

    run_command(ctx, handler, render)
