"""CI/CD commands."""

from __future__ import annotations

import typer
from pysourcecraft.models import GitRevision, RunWorkflowsRequest, WorkflowData

from sourcecraft_mcp.cli.common import RepoArg, render_fields, render_table, run_command, split_repo

app = typer.Typer(no_args_is_help=True)

RunSlugArg = typer.Argument(..., help="Slug CI-запуска.")
WorkflowSlugArg = typer.Argument(..., help="Имя workflow из конфига.")
TaskSlugArg = typer.Argument(..., help="Имя задачи.")
CubeSlugArg = typer.Argument(..., help="Имя cube.")


@app.command("runs")
def list_runs(
    ctx: typer.Context,
    repo: str = RepoArg,
    page_size: int = typer.Option(30, "--page-size"),
    page_token: str = typer.Option("", "--page-token"),
) -> None:
    """Список CI/CD запусков."""
    owner, name = split_repo(repo)

    async def handler(client):
        return await client.cicd.list_runs(
            owner=owner, repo=name, page_size=page_size, page_token=page_token or None
        )

    def render(result):
        runs = getattr(result, "runs", None) or []
        render_table(
            f"CI runs in {repo}",
            ["Slug", "Status", "Event", "Created"],
            [
                [
                    r.slug,
                    r.status,
                    r.event_type,
                    r.dates.created_at if r.dates else "",
                ]
                for r in runs
            ],
        )
        next_token = getattr(result, "next_page_token", None)
        if next_token:
            print(f"(Ещё результаты: --page-token '{next_token}')")

    run_command(ctx, handler, render)


@app.command("run")
def get_run(ctx: typer.Context, repo: str = RepoArg, run_slug: str = RunSlugArg) -> None:
    """Информация о CI запуске."""
    owner, name = split_repo(repo)

    async def handler(client):
        return await client.cicd.get_run(owner=owner, repo=name, run_slug=run_slug)

    def render(r):
        render_fields(
            f"CI run {r.slug}",
            [
                ("Status", r.status),
                ("Event", r.event_type),
                ("Created", r.dates.created_at if r.dates else None),
                ("Started", r.dates.started_at if r.dates else None),
                ("Finished", r.dates.finished_at if r.dates else None),
                ("Triggered by", f"@{r.user.slug}" if r.user else None),
                ("Pull request", f"#{r.pull.slug}" if r.pull else None),
            ],
        )
        if r.workflows:
            render_table(
                "Workflows",
                ["Slug", "Status", "Progress"],
                [
                    [
                        w.slug,
                        w.status,
                        f"{w.progress.percent:.0%}" if w.progress else "",
                    ]
                    for w in r.workflows
                ],
            )
        if r.error_messages:
            print("Errors: " + ", ".join(r.error_messages))

    run_command(ctx, handler, render)


@app.command("workflow")
def get_workflow(
    ctx: typer.Context,
    repo: str = RepoArg,
    run_slug: str = RunSlugArg,
    workflow_slug: str = WorkflowSlugArg,
) -> None:
    """Информация о workflow в CI запуске."""
    owner, name = split_repo(repo)

    async def handler(client):
        return await client.cicd.get_workflow(
            owner=owner, repo=name, run_slug=run_slug, workflow_slug=workflow_slug
        )

    def render(w):
        render_fields(
            f"Workflow {w.slug}",
            [
                ("Status", w.status),
                ("Description", w.description),
                ("Created", w.dates.created_at if w.dates else None),
                ("Started", w.dates.started_at if w.dates else None),
                ("Finished", w.dates.finished_at if w.dates else None),
                ("Progress", f"{w.progress.percent:.0%}" if w.progress else None),
                (
                    "Current step",
                    w.progress.current_cube.slug
                    if w.progress and w.progress.current_cube
                    else None,
                ),
            ],
        )
        if w.tasks:
            render_table("Tasks", ["Slug", "Status"], [[t.slug, t.status] for t in w.tasks])

    run_command(ctx, handler, render)


@app.command("logs")
def cube_logs(
    ctx: typer.Context,
    repo: str = RepoArg,
    run_slug: str = RunSlugArg,
    workflow_slug: str = WorkflowSlugArg,
    task_slug: str = TaskSlugArg,
    cube_slug: str = CubeSlugArg,
    page: int = typer.Option(1, "--page"),
) -> None:
    """Логи CI cube."""
    owner, name = split_repo(repo)

    async def handler(client):
        return await client.cicd.get_cube_logs(
            owner=owner,
            repo=name,
            run_slug=run_slug,
            workflow_slug=workflow_slug,
            task_slug=task_slug,
            cube_slug=cube_slug,
            page=page,
        )

    def render(result):
        print(result.logs or "No logs available")
        if not result.done:
            print(f"(Ещё логи: --page {page + 1})")

    run_command(ctx, handler, render)


@app.command("artifacts")
def artifacts(
    ctx: typer.Context,
    repo: str = RepoArg,
    run_slug: str = RunSlugArg,
    workflow_slug: str = WorkflowSlugArg,
    task_slug: str = TaskSlugArg,
    cube_slug: str = CubeSlugArg,
) -> None:
    """Артефакты CI cube."""
    owner, name = split_repo(repo)

    async def handler(client):
        return await client.cicd.get_artifacts(
            owner=owner,
            repo=name,
            run_slug=run_slug,
            workflow_slug=workflow_slug,
            task_slug=task_slug,
            cube_slug=cube_slug,
        )

    def render(result):
        items = getattr(result, "artifacts", None) or []
        render_table(
            f"Artifacts of {cube_slug}",
            ["Path", "Status", "Download URL"],
            [[a.local_path or a.id, a.status, a.download_url] for a in items],
        )

    run_command(ctx, handler, render)


@app.command("trigger")
def trigger(
    ctx: typer.Context,
    repo: str = RepoArg,
    workflows: list[str] = typer.Argument(..., help="Имена workflows для запуска."),
    branch: str = typer.Option("", "--branch", "-b", help="Ветка."),
    tag: str = typer.Option("", "--tag", help="Тег."),
    commit: str = typer.Option("", "--commit", help="SHA коммита."),
) -> None:
    """Запустить CI workflows."""
    owner, name = split_repo(repo)

    async def handler(client):
        head = GitRevision()
        if branch:
            head = GitRevision(branch=branch)
        elif tag:
            head = GitRevision(tag=tag)
        elif commit:
            head = GitRevision(commit=commit)
        request = RunWorkflowsRequest(
            head=head, workflows=[WorkflowData(name=w) for w in workflows]
        )
        return await client.cicd.run_workflows(owner=owner, repo=name, request=request)

    def render(r):
        render_fields(
            "Run triggered",
            [("Slug", r.slug), ("Status", r.status)],
        )

    run_command(ctx, handler, render)
