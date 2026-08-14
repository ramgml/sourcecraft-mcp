"""Issue commands."""

from __future__ import annotations

import typer
from pysourcecraft.models import CreateIssueRequest, IssueFilters, UpdateIssueRequest

from sourcecraft_mcp.cli.common import RepoArg, render_fields, render_table, run_command, split_repo

app = typer.Typer(no_args_is_help=True)


@app.command("list")
def list_issues(
    ctx: typer.Context,
    repo: str = RepoArg,
    status: str | None = typer.Option(
        None, "--status", "-s", help="open, inProgress, paused, closed, ..."
    ),
    assignee: str | None = typer.Option(None, "--assignee", "-a", help="ID исполнителя."),
    label: str | None = typer.Option(None, "--label", "-l", help="Slug метки."),
    page: int = typer.Option(1, "--page"),
    per_page: int = typer.Option(30, "--per-page"),
) -> None:
    """Список issues в репозитории."""
    owner, name = split_repo(repo)

    async def handler(client):
        filters = IssueFilters()
        if status:
            filters.state = status
        if assignee:
            filters.assignee_id = assignee
        if label:
            filters.label_ids = [label]
        return await client.issues.list(
            owner=owner, repo=name, filters=filters, page=page, per_page=per_page
        )

    def render(result):
        issues = getattr(result, "data", None) or []
        render_table(
            f"Issues in {repo}",
            ["#", "Title", "Status", "Priority", "Assignee"],
            [
                [
                    i.slug,
                    i.title,
                    i.status.name if i.status else "",
                    i.priority or "normal",
                    f"@{i.assignee.slug}" if i.assignee else "",
                ]
                for i in issues
            ],
        )

    run_command(ctx, handler, render)


@app.command("get")
def get_issue(
    ctx: typer.Context,
    repo: str = RepoArg,
    number: int = typer.Argument(..., help="Номер issue."),
) -> None:
    """Информация об issue."""
    owner, name = split_repo(repo)

    async def handler(client):
        return await client.issues.get(owner=owner, repo=name, issue_number=number)

    def render(i):
        render_fields(
            f"Issue #{i.slug}: {i.title}",
            [
                ("Status", i.status.name if i.status else None),
                ("Priority", i.priority or "normal"),
                ("Author", f"@{i.author.slug}" if i.author else None),
                ("Assignee", f"@{i.assignee.slug}" if i.assignee else None),
                ("Labels", ", ".join(label.name for label in i.labels) if i.labels else None),
                ("Description", i.description),
                ("Created", i.created_at),
                ("Updated", i.updated_at),
            ],
        )

    run_command(ctx, handler, render)


@app.command("create")
def create_issue(
    ctx: typer.Context,
    repo: str = RepoArg,
    title: str = typer.Option(..., "--title", "-t", help="Заголовок issue."),
    body: str = typer.Option("", "--body", "-b", help="Описание."),
    assignee: str | None = typer.Option(None, "--assignee", "-a", help="ID исполнителя."),
    label: list[str] | None = typer.Option(None, "--label", "-l", help="Slug метки."),
) -> None:
    """Создать issue."""
    owner, name = split_repo(repo)

    async def handler(client):
        request = CreateIssueRequest(
            title=title,
            body=body or None,
            assignee_ids=[assignee] if assignee else None,
            label_ids=label or None,
        )
        return await client.issues.create(owner=owner, repo=name, request=request)

    def render(i):
        render_fields(
            "Issue created",
            [
                ("#", i.slug),
                ("Title", i.title),
                ("Status", i.status.name if i.status else None),
                ("Author", f"@{i.author.slug}" if i.author else None),
            ],
        )

    run_command(ctx, handler, render)


@app.command("update")
def update_issue(
    ctx: typer.Context,
    repo: str = RepoArg,
    number: int = typer.Argument(..., help="Номер issue."),
    title: str | None = typer.Option(None, "--title", "-t"),
    body: str | None = typer.Option(None, "--body", "-b"),
    status: str | None = typer.Option(None, "--status", "-s", help="Slug нового статуса."),
    assignee: str | None = typer.Option(None, "--assignee", "-a"),
) -> None:
    """Обновить issue."""
    owner, name = split_repo(repo)

    async def handler(client):
        request = UpdateIssueRequest()
        if title is not None:
            request.title = title
        if body is not None:
            request.body = body or None
        if status is not None:
            request.state = status
        if assignee is not None:
            request.assignee_ids = [assignee] if assignee else None
        return await client.issues.update(
            owner=owner, repo=name, issue_number=number, request=request
        )

    def render(i):
        render_fields(
            "Issue updated",
            [
                ("#", i.slug),
                ("Title", i.title),
                ("Status", i.status.name if i.status else None),
            ],
        )

    run_command(ctx, handler, render)


@app.command("close")
def close_issue(
    ctx: typer.Context,
    repo: str = RepoArg,
    number: int = typer.Argument(..., help="Номер issue."),
) -> None:
    """Закрыть issue."""
    owner, name = split_repo(repo)

    async def handler(client):
        await client.issues.close(owner=owner, repo=name, issue_number=number)
        return {"closed": number}

    run_command(ctx, handler, lambda r: print(f"Issue #{r['closed']} closed"))


@app.command("reopen")
def reopen_issue(
    ctx: typer.Context,
    repo: str = RepoArg,
    number: int = typer.Argument(..., help="Номер issue."),
) -> None:
    """Переоткрыть issue."""
    owner, name = split_repo(repo)

    async def handler(client):
        await client.issues.reopen(owner=owner, repo=name, issue_number=number)
        return {"reopened": number}

    run_command(ctx, handler, lambda r: print(f"Issue #{r['reopened']} reopened"))


@app.command("comments")
def list_comments(
    ctx: typer.Context,
    repo: str = RepoArg,
    number: int = typer.Argument(..., help="Номер issue."),
    page: int = typer.Option(1, "--page"),
    per_page: int = typer.Option(30, "--per-page"),
) -> None:
    """Список комментариев к issue."""
    owner, name = split_repo(repo)

    async def handler(client):
        return await client.issues.list_comments(
            owner=owner, repo=name, issue_number=number, page=page, per_page=per_page
        )

    def render(result):
        comments = getattr(result, "data", None) or []
        render_table(
            f"Comments on issue #{number}",
            ["Author", "Created", "Comment"],
            [
                [
                    f"@{c.author.slug}" if c.author else "",
                    c.created_at,
                    c.body,
                ]
                for c in comments
            ],
        )

    run_command(ctx, handler, render)


@app.command("comment")
def add_comment(
    ctx: typer.Context,
    repo: str = RepoArg,
    number: int = typer.Argument(..., help="Номер issue."),
    body: str = typer.Option(..., "--body", "-b", help="Текст комментария."),
) -> None:
    """Добавить комментарий к issue."""
    owner, name = split_repo(repo)

    async def handler(client):
        return await client.issues.create_comment(
            owner=owner, repo=name, issue_number=number, body=body
        )

    def render(c):
        author = c.author.slug if c.author else "unknown"
        print(f"Comment added to issue #{number} by @{author}")

    run_command(ctx, handler, render)
