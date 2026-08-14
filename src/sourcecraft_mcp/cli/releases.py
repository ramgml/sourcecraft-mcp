"""Release commands."""

from __future__ import annotations

import typer
from pysourcecraft.models import CreateReleaseRequest, UpdateReleaseRequest

from sourcecraft_mcp.cli.common import RepoArg, render_fields, render_table, run_command, split_repo

app = typer.Typer(no_args_is_help=True)

TagArg = typer.Argument(..., help="Тег релиза (например, v1.0.0).")


@app.command("list")
def list_releases(
    ctx: typer.Context,
    repo: str = RepoArg,
    page_size: int = typer.Option(30, "--page-size"),
    page_token: str = typer.Option("", "--page-token"),
) -> None:
    """Список релизов репозитория."""
    owner, name = split_repo(repo)

    async def handler(client):
        return await client.releases.list(
            owner=owner, repo=name, page_size=page_size, page_token=page_token or None
        )

    def render(result):
        releases = getattr(result, "releases", None) or []
        render_table(
            f"Releases in {repo}",
            ["Tag", "Title", "Status", "Latest", "Pre-release"],
            [
                [
                    r.tag,
                    r.title,
                    r.status,
                    "✔" if r.is_latest else "",
                    "✔" if r.is_pre_release else "",
                ]
                for r in releases
            ],
        )
        next_token = getattr(result, "next_page_token", None)
        if next_token:
            print(f"(Ещё результаты: --page-token '{next_token}')")

    run_command(ctx, handler, render)


def _render_release(r) -> None:
    render_fields(
        f"Release {r.tag}",
        [
            ("Title", r.title),
            ("Status", r.status),
            ("Author", f"@{r.author.slug}" if r.author else None),
            ("Commit", r.hash[:7] if r.hash else None),
            ("Latest", "yes" if r.is_latest else None),
            ("Pre-release", "yes" if r.is_pre_release else None),
            ("Created", r.created_at),
            ("Released", r.released_at),
        ],
    )
    if r.release_notes:
        print("\nRelease notes:\n" + r.release_notes)
    if r.assets:
        render_table("Assets", ["Name"], [[a.name] for a in r.assets])


@app.command("get")
def get_release(ctx: typer.Context, repo: str = RepoArg, tag: str = TagArg) -> None:
    """Информация о релизе по тегу."""
    owner, name = split_repo(repo)

    async def handler(client):
        return await client.releases.get_by_tag(owner=owner, repo=name, tag=tag)

    run_command(ctx, handler, _render_release)


@app.command("latest")
def latest_release(ctx: typer.Context, repo: str = RepoArg) -> None:
    """Последний релиз репозитория."""
    owner, name = split_repo(repo)

    async def handler(client):
        return await client.releases.get_latest(owner=owner, repo=name)

    run_command(ctx, handler, _render_release)


@app.command("create")
def create_release(
    ctx: typer.Context,
    repo: str = RepoArg,
    tag: str = TagArg,
    title: str = typer.Option(..., "--title", "-t", help="Название релиза."),
    notes: str = typer.Option("", "--notes", "-n", help="Release notes."),
    target: str = typer.Option("", "--target", help="Ветка для создания тега."),
    publish: bool = typer.Option(False, "--publish", help="Опубликовать сразу (иначе — draft)."),
) -> None:
    """Создать релиз."""
    owner, name = split_repo(repo)

    async def handler(client):
        request = CreateReleaseRequest(
            tag_name=tag,
            name=title,
            body=notes or None,
            target_commitish=target or None,
            draft=not publish,
        )
        return await client.releases.create(owner=owner, repo=name, request=request)

    def render(r):
        render_fields(
            f"Release created ({'published' if publish else 'draft'})",
            [
                ("Tag", r.tag),
                ("Title", r.title),
                ("Status", r.status),
                ("Author", f"@{r.author.slug}" if r.author else None),
            ],
        )

    run_command(ctx, handler, render)


@app.command("update")
def update_release(
    ctx: typer.Context,
    repo: str = RepoArg,
    tag: str = TagArg,
    title: str | None = typer.Option(None, "--title", "-t"),
    notes: str | None = typer.Option(None, "--notes", "-n"),
) -> None:
    """Обновить релиз."""
    owner, name = split_repo(repo)

    async def handler(client):
        request = UpdateReleaseRequest()
        if title is not None:
            request.name = title
        if notes is not None:
            request.body = notes
        return await client.releases.update_by_tag(owner=owner, repo=name, tag=tag, request=request)

    def render(r):
        render_fields(
            "Release updated",
            [("Tag", r.tag), ("Title", r.title), ("Status", r.status)],
        )

    run_command(ctx, handler, render)


@app.command("publish")
def publish_release(ctx: typer.Context, repo: str = RepoArg, tag: str = TagArg) -> None:
    """Опубликовать draft релиз."""
    owner, name = split_repo(repo)

    async def handler(client):
        return await client.releases.publish_by_tag(owner=owner, repo=name, tag=tag)

    run_command(ctx, handler, lambda r: print(f"Release {r.tag} published. Status: {r.status}"))


@app.command("discard")
def discard_release(ctx: typer.Context, repo: str = RepoArg, tag: str = TagArg) -> None:
    """Отклонить релиз."""
    owner, name = split_repo(repo)

    async def handler(client):
        return await client.releases.discard_by_tag(owner=owner, repo=name, tag=tag)

    run_command(ctx, handler, lambda r: print(f"Release {r.tag} discarded. Status: {r.status}"))
