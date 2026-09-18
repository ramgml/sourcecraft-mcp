"""CI/CD tools for SourceCraft MCP server."""

from __future__ import annotations

from mcp.server.fastmcp import Context
from pysourcecraft.models import GitRevision, RunWorkflowsRequest, WorkflowData


async def list_ci_runs(
    owner: str,
    repo: str,
    page_size: int = 30,
    page_token: str = "",
    ctx: Context | None = None,
) -> str:
    """List CI/CD runs in a repository.

    Args:
        owner: Repository owner
        repo: Repository name
        page_size: Maximum number of runs to return
        page_token: Token for pagination (from previous response)
    """
    assert ctx is not None
    client = ctx.request_context.lifespan_context.client

    try:
        result = await client.cicd.list_runs(
            owner=owner,
            repo=repo,
            page_size=page_size,
            page_token=page_token or None,
        )

        runs = result.runs if hasattr(result, "runs") else []
        if not runs:
            return f"No CI runs found in '{owner}/{repo}'"

        lines = [f"CI/CD runs in '{owner}/{repo}':"]
        for run in runs:
            status_icons = {
                "created": "⏳",
                "queued": "⏸️",
                "running": "🔄",
                "success": "✅",
                "failed": "❌",
                "cancelled": "🚫",
            }
            icon = status_icons.get(run.status, "❓")

            lines.append(
                f"{icon} Run #{run.slug} - {run.status}\n"
                f"   Event: {run.event_type}\n"
                f"   Created: {run.dates.created_at if run.dates else 'unknown'}"
            )

        if hasattr(result, "next_page_token") and result.next_page_token:
            lines.append(f"\n(More results available, use page_token='{result.next_page_token}')")

        return "\n\n".join(lines)
    except Exception as e:
        return f"Error listing CI runs: {e}"


async def get_ci_run(
    owner: str,
    repo: str,
    run_slug: str,
    ctx: Context | None = None,
) -> str:
    """Get detailed information about a CI run.

    Args:
        owner: Repository owner
        repo: Repository name
        run_slug: Run slug identifier
    """
    assert ctx is not None
    client = ctx.request_context.lifespan_context.client

    try:
        result = await client.cicd.get_run(
            owner=owner,
            repo=repo,
            run_slug=run_slug,
        )

        status_icons = {
            "created": "⏳",
            "queued": "⏸️",
            "running": "🔄",
            "success": "✅",
            "failed": "❌",
            "cancelled": "🚫",
        }
        icon = status_icons.get(result.status, "❓")

        lines = [
            f"{icon} CI Run #{result.slug}",
            f"Status: {result.status}",
            f"Event Type: {result.event_type}",
        ]

        if result.dates:
            lines.extend(
                [
                    f"Created: {result.dates.created_at or 'N/A'}",
                    f"Started: {result.dates.started_at or 'N/A'}",
                    f"Finished: {result.dates.finished_at or 'N/A'}",
                ]
            )

        if result.user:
            lines.append(f"Triggered by: @{result.user.slug}")

        if result.pull:
            lines.append(f"Pull Request: #{result.pull.slug}")

        if result.workflows:
            lines.append(f"\nWorkflows ({len(result.workflows)}):")
            for workflow in result.workflows:
                progress = f" - {workflow.progress.percent:.0%}" if workflow.progress else ""
                lines.append(f"  • {workflow.slug}: {workflow.status}{progress}")

        if result.error_messages:
            lines.append(f"\nErrors: {', '.join(result.error_messages)}")

        return "\n".join(lines)
    except Exception as e:
        return f"Error getting CI run: {e}"


async def get_workflow(
    owner: str,
    repo: str,
    run_slug: str,
    workflow_slug: str,
    ctx: Context | None = None,
) -> str:
    """Get detailed information about a workflow in a CI run.

    Args:
        owner: Repository owner
        repo: Repository name
        run_slug: Run slug identifier
        workflow_slug: Workflow name as defined in the config
    """
    assert ctx is not None
    client = ctx.request_context.lifespan_context.client

    try:
        result = await client.cicd.get_workflow(
            owner=owner,
            repo=repo,
            run_slug=run_slug,
            workflow_slug=workflow_slug,
        )

        lines = [
            f"Workflow: {result.slug}",
            f"Status: {result.status}",
        ]

        if result.description:
            lines.append(f"Description: {result.description}")

        if result.dates:
            lines.extend(
                [
                    f"Created: {result.dates.created_at or 'N/A'}",
                    f"Started: {result.dates.started_at or 'N/A'}",
                    f"Finished: {result.dates.finished_at or 'N/A'}",
                ]
            )

        if result.progress:
            lines.append(f"Progress: {result.progress.percent:.0%}")
            if result.progress.current_cube:
                lines.append(f"Current Step: {result.progress.current_cube.slug}")

        if result.tasks:
            lines.append(f"\nTasks ({len(result.tasks)}):")
            for task in result.tasks:
                lines.append(f"  • {task.slug}: {task.status}")

        return "\n".join(lines)
    except Exception as e:
        return f"Error getting workflow: {e}"


async def get_cube_logs(
    owner: str,
    repo: str,
    run_slug: str,
    workflow_slug: str,
    task_slug: str,
    cube_slug: str,
    page: int = 1,
    ctx: Context | None = None,
) -> str:
    """Get logs from a running CI cube.

    Args:
        owner: Repository owner
        repo: Repository name
        run_slug: Run slug identifier
        workflow_slug: Workflow name
        task_slug: Task name
        cube_slug: Cube name
        page: Page number for log pagination
    """
    assert ctx is not None
    client = ctx.request_context.lifespan_context.client

    try:
        result = await client.cicd.get_cube_logs(
            owner=owner,
            repo=repo,
            run_slug=run_slug,
            workflow_slug=workflow_slug,
            task_slug=task_slug,
            cube_slug=cube_slug,
            page=page,
        )

        lines = [
            f"Logs for {cube_slug} (page {page}):",
            "=" * 40,
        ]

        if result.logs:
            lines.append(result.logs)
        else:
            lines.append("No logs available")

        lines.append("=" * 40)

        if result.page_complete:
            lines.append("(Page complete)")
        if result.done:
            lines.append("(All logs retrieved)")

        return "\n".join(lines)
    except Exception as e:
        return f"Error getting cube logs: {e}"


async def get_artifacts(
    owner: str,
    repo: str,
    run_slug: str,
    workflow_slug: str,
    task_slug: str,
    cube_slug: str,
    ctx: Context | None = None,
) -> str:
    """Get artifacts from a CI cube.

    Args:
        owner: Repository owner
        repo: Repository name
        run_slug: Run slug identifier
        workflow_slug: Workflow name
        task_slug: Task name
        cube_slug: Cube name
    """
    assert ctx is not None
    client = ctx.request_context.lifespan_context.client

    try:
        result = await client.cicd.get_artifacts(
            owner=owner,
            repo=repo,
            run_slug=run_slug,
            workflow_slug=workflow_slug,
            task_slug=task_slug,
            cube_slug=cube_slug,
        )

        artifacts = result.artifacts if hasattr(result, "artifacts") else []
        if not artifacts:
            return f"No artifacts found for {cube_slug}"

        lines = [f"Artifacts from {cube_slug}:"]
        for artifact in artifacts:
            status_icon = "✅" if artifact.status == "ready" else "⏳"
            lines.append(
                f"{status_icon} {artifact.local_path or artifact.id}\n   Status: {artifact.status}"
            )
            if artifact.download_url:
                lines.append(f"   Download: {artifact.download_url}")

        return "\n\n".join(lines)
    except Exception as e:
        return f"Error getting artifacts: {e}"


async def trigger_workflows(
    owner: str,
    repo: str,
    workflows: list[str],
    branch: str = "",
    tag: str = "",
    commit: str = "",
    ctx: Context | None = None,
) -> str:
    """Trigger CI workflows in a repository.

    Args:
        owner: Repository owner
        repo: Repository name
        workflows: List of workflow names to run
        branch: Git branch to run on
        tag: Git tag to run on
        commit: Commit SHA to run on
    """
    assert ctx is not None
    client = ctx.request_context.lifespan_context.client

    try:
        head = GitRevision()
        if branch:
            head = GitRevision(branch=branch)
        elif tag:
            head = GitRevision(tag=tag)
        elif commit:
            head = GitRevision(commit=commit)

        request = RunWorkflowsRequest(
            head=head,
            workflows=[WorkflowData(name=name) for name in workflows],
        )
        result = await client.cicd.run_workflows(owner=owner, repo=repo, request=request)

        lines = [
            "Run triggered successfully!",
            f"Run slug: {result.slug}",
            f"Status: {result.status}",
        ]

        return "\n".join(lines)
    except Exception as e:
        return f"Error triggering workflows: {e}"


def register_tools(mcp):
    """Register CI/CD tools with the MCP server."""

    @mcp.tool()
    async def _list_ci_runs(
        owner: str,
        repo: str,
        page_size: int = 30,
        page_token: str = "",
        ctx: Context | None = None,
    ) -> str:
        return await list_ci_runs(
            owner=owner,
            repo=repo,
            page_size=page_size,
            page_token=page_token,
            ctx=ctx,
        )

    @mcp.tool()
    async def _get_ci_run(
        owner: str,
        repo: str,
        run_slug: str,
        ctx: Context | None = None,
    ) -> str:
        return await get_ci_run(
            owner=owner,
            repo=repo,
            run_slug=run_slug,
            ctx=ctx,
        )

    @mcp.tool()
    async def _get_workflow(
        owner: str,
        repo: str,
        run_slug: str,
        workflow_slug: str,
        ctx: Context | None = None,
    ) -> str:
        return await get_workflow(
            owner=owner,
            repo=repo,
            run_slug=run_slug,
            workflow_slug=workflow_slug,
            ctx=ctx,
        )

    @mcp.tool()
    async def _get_cube_logs(
        owner: str,
        repo: str,
        run_slug: str,
        workflow_slug: str,
        task_slug: str,
        cube_slug: str,
        page: int = 1,
        ctx: Context | None = None,
    ) -> str:
        return await get_cube_logs(
            owner=owner,
            repo=repo,
            run_slug=run_slug,
            workflow_slug=workflow_slug,
            task_slug=task_slug,
            cube_slug=cube_slug,
            page=page,
            ctx=ctx,
        )

    @mcp.tool()
    async def _get_artifacts(
        owner: str,
        repo: str,
        run_slug: str,
        workflow_slug: str,
        task_slug: str,
        cube_slug: str,
        ctx: Context | None = None,
    ) -> str:
        return await get_artifacts(
            owner=owner,
            repo=repo,
            run_slug=run_slug,
            workflow_slug=workflow_slug,
            task_slug=task_slug,
            cube_slug=cube_slug,
            ctx=ctx,
        )

    @mcp.tool()
    async def _trigger_workflows(
        owner: str,
        repo: str,
        workflows: list[str],
        branch: str = "",
        tag: str = "",
        commit: str = "",
        ctx: Context | None = None,
    ) -> str:
        return await trigger_workflows(
            owner=owner,
            repo=repo,
            workflows=workflows,
            branch=branch,
            tag=tag,
            commit=commit,
            ctx=ctx,
        )
