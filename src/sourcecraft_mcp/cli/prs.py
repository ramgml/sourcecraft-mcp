"""Pull request commands."""

from __future__ import annotations

import typer
from pysourcecraft.models import (
    CreatePullRequestRequest,
    MergePullRequestRequest,
    PRFilters,
    PRMergeMethod,
    PRState,
    UpdatePullRequestRequest,
)

from sourcecraft_mcp.cli.common import RepoArg, render_fields, render_table, run_command, split_repo

app = typer.Typer(no_args_is_help=True)

PRNumberArg = typer.Argument(..., help="Номер pull request.")


@app.command("list")
def list_prs(
    ctx: typer.Context,
    repo: str = RepoArg,
    status: str | None = typer.Option(
        None, "--status", "-s", help="draft, open, merging, merged, discarded"
    ),
    author: str | None = typer.Option(None, "--author", "-a", help="ID автора."),
    source_branch: str | None = typer.Option(None, "--source", help="Исходная ветка."),
    target_branch: str | None = typer.Option(None, "--target", help="Целевая ветка."),
    page: int = typer.Option(1, "--page"),
    per_page: int = typer.Option(30, "--per-page"),
) -> None:
    """Список pull requests в репозитории."""
    owner, name = split_repo(repo)

    async def handler(client):
        filters = PRFilters()
        if status:
            filters.state = PRState(status)
        if author:
            filters.author_id = author
        if source_branch:
            filters.source_branch = source_branch
        if target_branch:
            filters.target_branch = target_branch
        return await client.pull_requests.list(
            owner=owner, repo=name, filters=filters, page=page, per_page=per_page
        )

    def render(result):
        prs = getattr(result, "data", None) or []
        render_table(
            f"Pull requests in {repo}",
            ["#", "Title", "Status", "Branch", "Author"],
            [
                [
                    p.slug,
                    p.title,
                    p.status,
                    f"{p.source_branch} → {p.target_branch}",
                    f"@{p.author.slug}" if p.author else "",
                ]
                for p in prs
            ],
        )

    run_command(ctx, handler, render)


@app.command("get")
def get_pr(ctx: typer.Context, repo: str = RepoArg, number: int = PRNumberArg) -> None:
    """Информация о pull request."""
    owner, name = split_repo(repo)

    async def handler(client):
        return await client.pull_requests.get(owner=owner, repo=name, pull_number=number)

    def render(p):
        render_fields(
            f"PR #{p.slug}: {p.title}",
            [
                ("Status", p.status),
                ("Author", f"@{p.author.slug}" if p.author else None),
                ("Source", p.source_branch),
                ("Target", p.target_branch),
                ("Description", p.description),
                (
                    "Merge commit",
                    p.merge_info.merge_commit_hash[:7]
                    if p.merge_info and p.merge_info.merge_commit_hash
                    else None,
                ),
                ("Created", p.created_at),
                ("Updated", p.updated_at),
            ],
        )

    run_command(ctx, handler, render)


@app.command("create")
def create_pr(
    ctx: typer.Context,
    repo: str = RepoArg,
    title: str = typer.Option(..., "--title", "-t", help="Заголовок PR."),
    source: str = typer.Option(..., "--source", help="Исходная ветка."),
    target: str = typer.Option(..., "--target", help="Целевая ветка."),
    description: str = typer.Option("", "--description", "-d"),
    reviewer: list[str] | None = typer.Option(None, "--reviewer", help="ID ревьюера."),
    publish: bool = typer.Option(False, "--publish", help="Опубликовать сразу (иначе — draft)."),
) -> None:
    """Создать pull request."""
    owner, name = split_repo(repo)

    async def handler(client):
        request = CreatePullRequestRequest(
            title=title,
            source_branch=source,
            target_branch=target,
            description=description or None,
            reviewer_ids=reviewer or None,
            publish=publish,
        )
        return await client.pull_requests.create(owner=owner, repo=name, request=request)

    def render(p):
        render_fields(
            f"PR created ({'published' if publish else 'draft'})",
            [
                ("#", p.slug),
                ("Title", p.title),
                ("Branch", f"{p.source_branch} → {p.target_branch}"),
                ("Author", f"@{p.author.slug}" if p.author else None),
            ],
        )

    run_command(ctx, handler, render)


@app.command("update")
def update_pr(
    ctx: typer.Context,
    repo: str = RepoArg,
    number: int = PRNumberArg,
    title: str | None = typer.Option(None, "--title", "-t"),
    description: str | None = typer.Option(None, "--description", "-d"),
) -> None:
    """Обновить pull request."""
    owner, name = split_repo(repo)

    async def handler(client):
        request = UpdatePullRequestRequest()
        if title is not None:
            request.title = title
        if description is not None:
            request.description = description
        return await client.pull_requests.update(
            owner=owner, repo=name, pull_number=number, request=request
        )

    def render(p):
        render_fields("PR updated", [("#", p.slug), ("Title", p.title)])

    run_command(ctx, handler, render)


@app.command("merge")
def merge_pr(
    ctx: typer.Context,
    repo: str = RepoArg,
    number: int = PRNumberArg,
    commit_title: str = typer.Option("", "--commit-title", help="Заголовок merge-коммита."),
    commit_message: str = typer.Option("", "--commit-message", help="Текст merge-коммита."),
    squash: bool = typer.Option(False, "--squash", help="Сквошить коммиты."),
) -> None:
    """Смержить pull request."""
    owner, name = split_repo(repo)

    async def handler(client):
        request = MergePullRequestRequest(
            commit_title=commit_title or None,
            commit_message=commit_message or None,
            method=PRMergeMethod.SQUASH if squash else PRMergeMethod.MERGE,
        )
        return await client.pull_requests.merge(
            owner=owner, repo=name, pull_number=number, request=request
        )

    def render(p):
        commit = (
            p.merge_info.merge_commit_hash[:7]
            if p.merge_info and p.merge_info.merge_commit_hash
            else ""
        )
        print(f"PR #{number} merged" + (f" (commit {commit})" if commit else ""))

    run_command(ctx, handler, render)


@app.command("publish")
def publish_pr(ctx: typer.Context, repo: str = RepoArg, number: int = PRNumberArg) -> None:
    """Опубликовать draft pull request."""
    owner, name = split_repo(repo)

    async def handler(client):
        return await client.pull_requests.publish(owner=owner, repo=name, pull_number=number)

    run_command(ctx, handler, lambda p: print(f"PR #{number} published. Status: {p.status}"))


@app.command("discard")
def discard_pr(ctx: typer.Context, repo: str = RepoArg, number: int = PRNumberArg) -> None:
    """Отклонить (закрыть) pull request."""
    owner, name = split_repo(repo)

    async def handler(client):
        return await client.pull_requests.discard(owner=owner, repo=name, pull_number=number)

    run_command(ctx, handler, lambda p: print(f"PR #{number} discarded. Status: {p.status}"))


@app.command("reviewers")
def list_reviewers(ctx: typer.Context, repo: str = RepoArg, number: int = PRNumberArg) -> None:
    """Список ревьюеров pull request."""
    owner, name = split_repo(repo)

    async def handler(client):
        return await client.pull_requests.list_reviewers(owner=owner, repo=name, pull_number=number)

    def render(result):
        reviewers = getattr(result, "reviewers", None) or []
        render_table(
            f"Reviewers of PR #{number}",
            ["User", "Decision"],
            [
                [f"@{r.user.slug}" if r.user else "", r.review_decision or "no decision"]
                for r in reviewers
            ],
        )

    run_command(ctx, handler, render)


@app.command("add-reviewer")
def add_reviewer(
    ctx: typer.Context,
    repo: str = RepoArg,
    number: int = PRNumberArg,
    user_id: str = typer.Option(..., "--user", "-u", help="ID пользователя."),
) -> None:
    """Добавить ревьюера к pull request."""
    owner, name = split_repo(repo)

    async def handler(client):
        await client.pull_requests.add_reviewer(
            owner=owner, repo=name, pull_number=number, user_id=user_id
        )
        return {"user": user_id}

    run_command(ctx, handler, lambda r: print(f"Reviewer {r['user']} added to PR #{number}"))


@app.command("review")
def set_review(
    ctx: typer.Context,
    repo: str = RepoArg,
    number: int = PRNumberArg,
    decision: str = typer.Option(..., "--decision", "-d", help="approve | trust | block | abstain"),
) -> None:
    """Установить решение ревью на pull request."""
    owner, name = split_repo(repo)

    async def handler(client):
        await client.pull_requests.set_review_decision(
            owner=owner, repo=name, pull_number=number, decision=decision
        )
        return {"decision": decision}

    def render(r):
        print(f"Review decision '{r['decision']}' set on PR #{number}")

    run_command(ctx, handler, render)
