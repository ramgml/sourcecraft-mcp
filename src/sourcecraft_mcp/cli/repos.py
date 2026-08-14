"""Repository commands."""

from __future__ import annotations

import typer
from pysourcecraft.models import CreateRepositoryRequest, RepoVisibility, UpdateRepositoryRequest

from sourcecraft_mcp.cli.common import RepoArg, render_fields, render_table, run_command, split_repo

app = typer.Typer(no_args_is_help=True)


@app.command("list")
def list_repos(
    ctx: typer.Context,
    org: str | None = typer.Option(None, "--org", help="Список репозиториев организации."),
    username: str | None = typer.Option(
        None, "--user", help="Список репозиториев пользователя (по умолчанию — свои)."
    ),
    page: int = typer.Option(1, "--page", help="Номер страницы."),
    per_page: int = typer.Option(30, "--per-page", help="Элементов на странице."),
) -> None:
    """Список репозиториев (своих, пользователя или организации)."""

    async def handler(client):
        if org:
            return await client.repositories.list_org_repos(org=org, page=page, per_page=per_page)
        return await client.repositories.list(username=username, page=page, per_page=per_page)

    def render(result):
        repos = getattr(result, "repositories", None) or []
        render_table(
            "Repositories",
            ["Slug", "Name", "Visibility", "Description"],
            [[r.slug, r.name, r.visibility, r.description] for r in repos],
        )

    run_command(ctx, handler, render)


@app.command("get")
def get_repo(ctx: typer.Context, repo: str = RepoArg) -> None:
    """Информация о репозитории."""
    owner, name = split_repo(repo)

    async def handler(client):
        return await client.repositories.get(owner=owner, repo=name)

    def render(r):
        render_fields(
            f"Repository {r.slug}",
            [
                ("Name", r.name),
                ("Visibility", r.visibility),
                ("Description", r.description),
                ("Default branch", r.default_branch),
                ("Language", r.language.name if r.language else None),
                ("Web URL", r.web_url),
                ("Clone (SSH)", r.clone_url.ssh if r.clone_url else None),
                ("Clone (HTTPS)", r.clone_url.https if r.clone_url else None),
                ("Last updated", r.last_updated),
            ],
        )

    run_command(ctx, handler, render)


@app.command("create")
def create_repo(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="Имя репозитория."),
    description: str = typer.Option("", "--description", "-d", help="Описание."),
    visibility: str = typer.Option(
        "private", "--visibility", "-v", help="public | internal | private"
    ),
) -> None:
    """Создать репозиторий."""

    async def handler(client):
        request = CreateRepositoryRequest(
            name=name,
            description=description or None,
            visibility=RepoVisibility(visibility),
        )
        return await client.repositories.create(request=request)

    def render(r):
        render_fields(
            "Repository created",
            [
                ("Slug", r.slug),
                ("Name", r.name),
                ("Visibility", r.visibility),
                ("Web URL", r.web_url),
                ("Clone (SSH)", r.clone_url.ssh if r.clone_url else None),
            ],
        )

    run_command(ctx, handler, render)


@app.command("update")
def update_repo(
    ctx: typer.Context,
    repo: str = RepoArg,
    description: str | None = typer.Option(None, "--description", "-d"),
    default_branch: str | None = typer.Option(None, "--default-branch"),
    visibility: str | None = typer.Option(None, "--visibility", "-v"),
) -> None:
    """Обновить настройки репозитория."""
    owner, name = split_repo(repo)

    async def handler(client):
        request = UpdateRepositoryRequest()
        if description is not None:
            request.description = description
        if default_branch is not None:
            request.default_branch = default_branch
        if visibility is not None:
            request.visibility = RepoVisibility(visibility)
        return await client.repositories.update(owner=owner, repo=name, request=request)

    def render(r):
        render_fields(
            "Repository updated",
            [
                ("Slug", r.slug),
                ("Description", r.description),
                ("Default branch", r.default_branch),
                ("Visibility", r.visibility),
            ],
        )

    run_command(ctx, handler, render)


@app.command("delete")
def delete_repo(
    ctx: typer.Context,
    repo: str = RepoArg,
    yes: bool = typer.Option(False, "--yes", "-y", help="Не запрашивать подтверждение."),
) -> None:
    """Удалить репозиторий."""
    owner, name = split_repo(repo)
    if not yes:
        typer.confirm(f"Удалить репозиторий '{owner}/{name}'?", abort=True)

    async def handler(client):
        await client.repositories.delete(owner=owner, repo=name)
        return {"deleted": f"{owner}/{name}"}

    run_command(ctx, handler, lambda r: print(f"Repository '{r['deleted']}' deleted"))


@app.command("branches")
def list_branches(
    ctx: typer.Context,
    repo: str = RepoArg,
    page: int = typer.Option(1, "--page"),
    per_page: int = typer.Option(30, "--per-page"),
) -> None:
    """Список веток репозитория."""
    owner, name = split_repo(repo)

    async def handler(client):
        return await client.repositories.list_branches(
            owner=owner, repo=name, page=page, per_page=per_page
        )

    def render(result):
        branches = getattr(result, "branches", None) or []
        render_table(
            f"Branches in {repo}",
            ["Name", "Commit"],
            [[b.name, b.commit.hash[:7] if b.commit else ""] for b in branches],
        )

    run_command(ctx, handler, render)


@app.command("tags")
def list_tags(
    ctx: typer.Context,
    repo: str = RepoArg,
    page: int = typer.Option(1, "--page"),
    per_page: int = typer.Option(30, "--per-page"),
) -> None:
    """Список тегов репозитория."""
    owner, name = split_repo(repo)

    async def handler(client):
        return await client.repositories.list_tags(
            owner=owner, repo=name, page=page, per_page=per_page
        )

    def render(result):
        tags = getattr(result, "tags", None) or []
        render_table(
            f"Tags in {repo}",
            ["Name", "Commit"],
            [[t.name, t.commit.hash[:7] if t.commit else ""] for t in tags],
        )

    run_command(ctx, handler, render)


@app.command("tree")
def file_tree(
    ctx: typer.Context,
    repo: str = RepoArg,
    revision: str = typer.Option("", "--revision", "-r", help="Ветка, тег или SHA коммита."),
    path: str = typer.Option("", "--path", "-p", help="Путь внутри репозитория."),
    recursive: bool = typer.Option(False, "--recursive", "-R", help="Рекурсивный вывод."),
) -> None:
    """Дерево файлов репозитория."""
    owner, name = split_repo(repo)

    async def handler(client):
        return await client.repositories.get_file_tree(
            owner=owner,
            repo=name,
            revision=revision or None,
            path=path or None,
            recursive=recursive,
        )

    def render(result):
        trees = getattr(result, "trees", None) or []
        render_table(
            f"Files in {repo}:{path or '/'}",
            ["Type", "Path"],
            [[t.type, t.path] for t in trees],
        )

    run_command(ctx, handler, render)
