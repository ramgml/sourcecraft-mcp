"""Tests for CI/CD tools."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from pysourcecraft.models import GitRevision, WorkflowData

from sourcecraft_mcp.tools import cicd


class TestListCiRuns:
    """Test list_ci_runs tool."""

    @pytest.mark.asyncio
    async def test_list_ci_runs_success(self, mock_client, mock_context):
        """Test successful CI runs listing."""
        mock_run1 = MagicMock()
        mock_run1.slug = "run-1"
        mock_run1.status = "success"
        mock_run1.event_type = "push"
        mock_run1.dates = MagicMock()
        mock_run1.dates.created_at = "2024-01-15T10:00:00Z"

        mock_run2 = MagicMock()
        mock_run2.slug = "run-2"
        mock_run2.status = "failed"
        mock_run2.event_type = "pull_request"
        mock_run2.dates = None

        mock_result = MagicMock()
        mock_result.runs = [mock_run1, mock_run2]

        mock_client.cicd.list_runs = AsyncMock(return_value=mock_result)

        result = await cicd.list_ci_runs(owner="test", repo="test-repo", ctx=mock_context)

        assert "CI/CD runs in 'test/test-repo'" in result
        assert "Run #run-1" in result
        assert "Run #run-2" in result
        assert "success" in result
        assert "failed" in result

    @pytest.mark.asyncio
    async def test_list_ci_runs_all_statuses(self, mock_client, mock_context):
        """Test CI runs with all possible statuses."""
        statuses = ["created", "queued", "running", "success", "failed", "cancelled", "unknown"]
        runs = []
        for status in statuses:
            run = MagicMock()
            run.slug = f"run-{status}"
            run.status = status
            run.event_type = "push"
            run.dates = MagicMock()
            run.dates.created_at = "2024-01-15T10:00:00Z"
            runs.append(run)

        mock_result = MagicMock()
        mock_result.runs = runs

        mock_client.cicd.list_runs = AsyncMock(return_value=mock_result)

        result = await cicd.list_ci_runs(owner="test", repo="test-repo", ctx=mock_context)

        assert "⏳" in result  # created
        assert "⏸️" in result  # queued
        assert "🔄" in result  # running
        assert "✅" in result  # success
        assert "❌" in result  # failed
        assert "🚫" in result  # cancelled
        assert "❓" in result  # unknown

    @pytest.mark.asyncio
    async def test_list_ci_runs_empty(self, mock_client, mock_context):
        """Test listing with no CI runs."""
        mock_result = MagicMock()
        mock_result.runs = []

        mock_client.cicd.list_runs = AsyncMock(return_value=mock_result)

        result = await cicd.list_ci_runs(owner="test", repo="test-repo", ctx=mock_context)

        assert "No CI runs found in 'test/test-repo'" == result

    @pytest.mark.asyncio
    async def test_list_ci_runs_no_runs_attr(self, mock_client, mock_context):
        """Test when result has no runs attribute."""
        mock_result = MagicMock()
        del mock_result.runs

        mock_client.cicd.list_runs = AsyncMock(return_value=mock_result)

        result = await cicd.list_ci_runs(owner="test", repo="test-repo", ctx=mock_context)

        assert "No CI runs found in 'test/test-repo'" == result

    @pytest.mark.asyncio
    async def test_list_ci_runs_with_pagination_token(self, mock_client, mock_context):
        """Test listing with pagination token."""
        mock_run = MagicMock()
        mock_run.slug = "run-1"
        mock_run.status = "success"
        mock_run.event_type = "push"
        mock_run.dates = MagicMock()
        mock_run.dates.created_at = "2024-01-15T10:00:00Z"

        mock_result = MagicMock()
        mock_result.runs = [mock_run]
        mock_result.next_page_token = "next-token-123"

        mock_client.cicd.list_runs = AsyncMock(return_value=mock_result)

        result = await cicd.list_ci_runs(
            owner="test",
            repo="test-repo",
            page_size=10,
            page_token="initial-token",
            ctx=mock_context,
        )

        mock_client.cicd.list_runs.assert_called_once_with(
            owner="test",
            repo="test-repo",
            page_size=10,
            page_token="initial-token",
        )
        assert "next-token-123" in result

    @pytest.mark.asyncio
    async def test_list_ci_runs_empty_page_token(self, mock_client, mock_context):
        """Test that empty page_token is converted to None."""
        mock_result = MagicMock()
        mock_result.runs = []

        mock_client.cicd.list_runs = AsyncMock(return_value=mock_result)

        await cicd.list_ci_runs(owner="test", repo="test-repo", page_token="", ctx=mock_context)

        mock_client.cicd.list_runs.assert_called_once_with(
            owner="test",
            repo="test-repo",
            page_size=30,
            page_token=None,
        )

    @pytest.mark.asyncio
    async def test_list_ci_runs_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.cicd.list_runs = AsyncMock(side_effect=Exception("API Error"))

        result = await cicd.list_ci_runs(owner="test", repo="test-repo", ctx=mock_context)

        assert "Error listing CI runs" in result
        assert "API Error" in result


class TestGetCiRun:
    """Test get_ci_run tool."""

    @pytest.mark.asyncio
    async def test_get_ci_run_success_full(self, mock_client, mock_context):
        """Test successful CI run retrieval with all fields."""
        mock_run = MagicMock()
        mock_run.slug = "run-123"
        mock_run.status = "success"
        mock_run.event_type = "push"
        mock_run.dates = MagicMock()
        mock_run.dates.created_at = "2024-01-15T10:00:00Z"
        mock_run.dates.started_at = "2024-01-15T10:01:00Z"
        mock_run.dates.finished_at = "2024-01-15T10:05:00Z"
        mock_run.user = MagicMock()
        mock_run.user.slug = "testuser"
        mock_run.pull = MagicMock()
        mock_run.pull.slug = "pr-42"

        mock_workflow1 = MagicMock()
        mock_workflow1.slug = "build"
        mock_workflow1.status = "success"
        mock_workflow1.progress = MagicMock()
        mock_workflow1.progress.percent = 1.0

        mock_workflow2 = MagicMock()
        mock_workflow2.slug = "test"
        mock_workflow2.status = "success"
        mock_workflow2.progress = None

        mock_run.workflows = [mock_workflow1, mock_workflow2]
        mock_run.error_messages = []

        mock_client.cicd.get_run = AsyncMock(return_value=mock_run)

        result = await cicd.get_ci_run(
            owner="test", repo="test-repo", run_slug="run-123", ctx=mock_context
        )

        assert "CI Run #run-123" in result
        assert "success" in result
        assert "push" in result
        assert "testuser" in result
        assert "pr-42" in result
        assert "build" in result
        assert "test" in result
        assert "100%" in result

    @pytest.mark.asyncio
    async def test_get_ci_run_with_errors(self, mock_client, mock_context):
        """Test CI run with error messages."""
        mock_run = MagicMock()
        mock_run.slug = "run-456"
        mock_run.status = "failed"
        mock_run.event_type = "push"
        mock_run.dates = None
        mock_run.user = None
        mock_run.pull = None
        mock_run.workflows = []
        mock_run.error_messages = ["Build failed", "Test timeout"]

        mock_client.cicd.get_run = AsyncMock(return_value=mock_run)

        result = await cicd.get_ci_run(
            owner="test", repo="test-repo", run_slug="run-456", ctx=mock_context
        )

        assert "CI Run #run-456" in result
        assert "Build failed" in result
        assert "Test timeout" in result

    @pytest.mark.asyncio
    async def test_get_ci_run_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.cicd.get_run = AsyncMock(side_effect=Exception("API Error"))

        result = await cicd.get_ci_run(
            owner="test", repo="test-repo", run_slug="run-123", ctx=mock_context
        )

        assert "Error getting CI run" in result


class TestGetWorkflow:
    """Test get_workflow tool."""

    @pytest.mark.asyncio
    async def test_get_workflow_success_full(self, mock_client, mock_context):
        """Test successful workflow retrieval with all fields."""
        mock_workflow = MagicMock()
        mock_workflow.slug = "build-and-test"
        mock_workflow.status = "success"
        mock_workflow.description = "Build and test workflow"
        mock_workflow.dates = MagicMock()
        mock_workflow.dates.created_at = "2024-01-15T10:00:00Z"
        mock_workflow.dates.started_at = "2024-01-15T10:01:00Z"
        mock_workflow.dates.finished_at = "2024-01-15T10:10:00Z"
        mock_workflow.progress = MagicMock()
        mock_workflow.progress.percent = 1.0
        mock_workflow.progress.current_cube = MagicMock()
        mock_workflow.progress.current_cube.slug = "test-cube"

        mock_task1 = MagicMock()
        mock_task1.slug = "compile"
        mock_task1.status = "success"
        mock_task2 = MagicMock()
        mock_task2.slug = "test"
        mock_task2.status = "success"
        mock_workflow.tasks = [mock_task1, mock_task2]

        mock_client.cicd.get_workflow = AsyncMock(return_value=mock_workflow)

        result = await cicd.get_workflow(
            owner="test",
            repo="test-repo",
            run_slug="run-123",
            workflow_slug="build-and-test",
            ctx=mock_context,
        )

        assert "Workflow: build-and-test" in result
        assert "success" in result
        assert "Build and test workflow" in result
        assert "100%" in result
        assert "test-cube" in result
        assert "compile" in result
        assert "test" in result

    @pytest.mark.asyncio
    async def test_get_workflow_minimal(self, mock_client, mock_context):
        """Test workflow with minimal fields."""
        mock_workflow = MagicMock()
        mock_workflow.slug = "deploy"
        mock_workflow.status = "running"
        mock_workflow.description = None
        mock_workflow.dates = None
        mock_workflow.progress = None
        mock_workflow.tasks = []

        mock_client.cicd.get_workflow = AsyncMock(return_value=mock_workflow)

        result = await cicd.get_workflow(
            owner="test",
            repo="test-repo",
            run_slug="run-123",
            workflow_slug="deploy",
            ctx=mock_context,
        )

        assert "Workflow: deploy" in result
        assert "running" in result
        assert "Description" not in result

    @pytest.mark.asyncio
    async def test_get_workflow_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.cicd.get_workflow = AsyncMock(side_effect=Exception("API Error"))

        result = await cicd.get_workflow(
            owner="test",
            repo="test-repo",
            run_slug="run-123",
            workflow_slug="build",
            ctx=mock_context,
        )

        assert "Error getting workflow" in result


class TestGetCubeLogs:
    """Test get_cube_logs tool."""

    @pytest.mark.asyncio
    async def test_get_cube_logs_success(self, mock_client, mock_context):
        """Test successful logs retrieval."""
        mock_result = MagicMock()
        mock_result.logs = "Line 1\nLine 2\nLine 3"
        mock_result.page_complete = True
        mock_result.done = True

        mock_client.cicd.get_cube_logs = AsyncMock(return_value=mock_result)

        result = await cicd.get_cube_logs(
            owner="test",
            repo="test-repo",
            run_slug="run-123",
            workflow_slug="build",
            task_slug="compile",
            cube_slug="build-cube",
            page=2,
            ctx=mock_context,
        )

        mock_client.cicd.get_cube_logs.assert_called_once_with(
            owner="test",
            repo="test-repo",
            run_slug="run-123",
            workflow_slug="build",
            task_slug="compile",
            cube_slug="build-cube",
            page=2,
        )
        assert "Logs for build-cube (page 2)" in result
        assert "Line 1" in result
        assert "Page complete" in result
        assert "All logs retrieved" in result

    @pytest.mark.asyncio
    async def test_get_cube_logs_empty(self, mock_client, mock_context):
        """Test logs retrieval with no logs."""
        mock_result = MagicMock()
        mock_result.logs = None
        mock_result.page_complete = False
        mock_result.done = False

        mock_client.cicd.get_cube_logs = AsyncMock(return_value=mock_result)

        result = await cicd.get_cube_logs(
            owner="test",
            repo="test-repo",
            run_slug="run-123",
            workflow_slug="build",
            task_slug="compile",
            cube_slug="build-cube",
            ctx=mock_context,
        )

        assert "No logs available" in result
        assert "Page complete" not in result

    @pytest.mark.asyncio
    async def test_get_cube_logs_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.cicd.get_cube_logs = AsyncMock(side_effect=Exception("API Error"))

        result = await cicd.get_cube_logs(
            owner="test",
            repo="test-repo",
            run_slug="run-123",
            workflow_slug="build",
            task_slug="compile",
            cube_slug="build-cube",
            ctx=mock_context,
        )

        assert "Error getting cube logs" in result


class TestGetArtifacts:
    """Test get_artifacts tool."""

    @pytest.mark.asyncio
    async def test_get_artifacts_success(self, mock_client, mock_context):
        """Test successful artifacts retrieval."""
        mock_artifact1 = MagicMock()
        mock_artifact1.id = "art-1"
        mock_artifact1.local_path = "/output/build.zip"
        mock_artifact1.status = "ready"
        mock_artifact1.download_url = "https://example.com/art-1"

        mock_artifact2 = MagicMock()
        mock_artifact2.id = "art-2"
        mock_artifact2.local_path = None
        mock_artifact2.status = "processing"
        mock_artifact2.download_url = None

        mock_result = MagicMock()
        mock_result.artifacts = [mock_artifact1, mock_artifact2]

        mock_client.cicd.get_artifacts = AsyncMock(return_value=mock_result)

        result = await cicd.get_artifacts(
            owner="test",
            repo="test-repo",
            run_slug="run-123",
            workflow_slug="build",
            task_slug="compile",
            cube_slug="build-cube",
            ctx=mock_context,
        )

        assert "Artifacts from build-cube" in result
        assert "build.zip" in result
        assert "art-2" in result
        assert "ready" in result
        assert "processing" in result
        assert "https://example.com/art-1" in result

    @pytest.mark.asyncio
    async def test_get_artifacts_empty(self, mock_client, mock_context):
        """Test artifacts retrieval with no artifacts."""
        mock_result = MagicMock()
        mock_result.artifacts = []

        mock_client.cicd.get_artifacts = AsyncMock(return_value=mock_result)

        result = await cicd.get_artifacts(
            owner="test",
            repo="test-repo",
            run_slug="run-123",
            workflow_slug="build",
            task_slug="compile",
            cube_slug="build-cube",
            ctx=mock_context,
        )

        assert "No artifacts found for build-cube" == result

    @pytest.mark.asyncio
    async def test_get_artifacts_no_attr(self, mock_client, mock_context):
        """Test when result has no artifacts attribute."""
        mock_result = MagicMock()
        del mock_result.artifacts

        mock_client.cicd.get_artifacts = AsyncMock(return_value=mock_result)

        result = await cicd.get_artifacts(
            owner="test",
            repo="test-repo",
            run_slug="run-123",
            workflow_slug="build",
            task_slug="compile",
            cube_slug="build-cube",
            ctx=mock_context,
        )

        assert "No artifacts found for build-cube" == result

    @pytest.mark.asyncio
    async def test_get_artifacts_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.cicd.get_artifacts = AsyncMock(side_effect=Exception("API Error"))

        result = await cicd.get_artifacts(
            owner="test",
            repo="test-repo",
            run_slug="run-123",
            workflow_slug="build",
            task_slug="compile",
            cube_slug="build-cube",
            ctx=mock_context,
        )

        assert "Error getting artifacts" in result


class TestTriggerWorkflows:
    """Test trigger_workflows tool."""

    @pytest.mark.asyncio
    async def test_trigger_workflows_with_branch(self, mock_client, mock_context):
        """Test triggering workflows with branch."""
        mock_result = MagicMock()
        mock_result.slug = "12"
        mock_result.status = "created"

        mock_client.cicd.run_workflows = AsyncMock(return_value=mock_result)

        result = await cicd.trigger_workflows(
            owner="test",
            repo="test-repo",
            workflows=["build", "test"],
            branch="main",
            ctx=mock_context,
        )

        mock_client.cicd.run_workflows.assert_called_once()
        kwargs = mock_client.cicd.run_workflows.call_args.kwargs
        assert kwargs["owner"] == "test"
        assert kwargs["repo"] == "test-repo"
        body = kwargs["request"]
        assert body.head == GitRevision(branch="main")
        assert body.workflows == [
            WorkflowData(name="build"),
            WorkflowData(name="test"),
        ]
        assert "Run triggered successfully" in result
        assert "12" in result
        assert "created" in result

    @pytest.mark.asyncio
    async def test_trigger_workflows_with_tag(self, mock_client, mock_context):
        """Test triggering workflows with tag."""
        mock_result = MagicMock()
        mock_result.slug = "13"
        mock_result.status = "created"

        mock_client.cicd.run_workflows = AsyncMock(return_value=mock_result)

        await cicd.trigger_workflows(
            owner="test",
            repo="test-repo",
            workflows=["deploy"],
            tag="v1.0.0",
            ctx=mock_context,
        )

        body = mock_client.cicd.run_workflows.call_args.kwargs["request"]
        assert body.head == GitRevision(tag="v1.0.0")

    @pytest.mark.asyncio
    async def test_trigger_workflows_with_commit(self, mock_client, mock_context):
        """Test triggering workflows with commit."""
        mock_result = MagicMock()
        mock_result.slug = "14"
        mock_result.status = "created"

        mock_client.cicd.run_workflows = AsyncMock(return_value=mock_result)

        await cicd.trigger_workflows(
            owner="test",
            repo="test-repo",
            workflows=["test"],
            commit="abc123",
            ctx=mock_context,
        )

        body = mock_client.cicd.run_workflows.call_args.kwargs["request"]
        assert body.head == GitRevision(commit="abc123")

    @pytest.mark.asyncio
    async def test_trigger_workflows_defaults_to_empty_head(self, mock_client, mock_context):
        """Test that no ref means the server default branch (empty head)."""
        mock_result = MagicMock()
        mock_result.slug = "15"
        mock_result.status = "created"

        mock_client.cicd.run_workflows = AsyncMock(return_value=mock_result)

        await cicd.trigger_workflows(
            owner="test",
            repo="test-repo",
            workflows=["build"],
            ctx=mock_context,
        )

        body = mock_client.cicd.run_workflows.call_args.kwargs["request"]
        assert body.head == GitRevision()

    @pytest.mark.asyncio
    async def test_trigger_workflows_empty_workflows(self, mock_client, mock_context):
        """Test triggering workflows with empty list."""
        mock_result = MagicMock()
        mock_result.slug = "16"
        mock_result.status = "created"

        mock_client.cicd.run_workflows = AsyncMock(return_value=mock_result)

        await cicd.trigger_workflows(
            owner="test",
            repo="test-repo",
            workflows=[],
            branch="main",
            ctx=mock_context,
        )

        body = mock_client.cicd.run_workflows.call_args.kwargs["request"]
        assert body.workflows == []

    @pytest.mark.asyncio
    async def test_trigger_workflows_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.cicd.run_workflows = AsyncMock(side_effect=Exception("API Error"))

        result = await cicd.trigger_workflows(
            owner="test",
            repo="test-repo",
            workflows=["build"],
            ctx=mock_context,
        )

        assert "Error triggering workflows" in result


class TestRegisterTools:
    """Test register_tools function."""

    def test_register_tools_registers_all_tools(self) -> None:
        """Test that all tools are registered."""
        mock_mcp = MagicMock()
        tool_count: list[str] = []

        def capture_tool(func: object) -> object:
            tool_count.append(getattr(func, "__name__", str(func)))
            return func

        mock_mcp.tool = MagicMock(return_value=capture_tool)
        cicd.register_tools(mock_mcp)

        assert mock_mcp.tool.call_count == 6

    @pytest.mark.asyncio
    async def test_register_tools_list_ci_runs(self, mock_client) -> None:
        """Test that register_tools registers _list_ci_runs."""
        mock_mcp = MagicMock()
        mock_context = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_client

        tool_calls: list[tuple[str, object]] = []

        def mock_tool(**kwargs: object) -> object:
            def decorator(func: object) -> object:
                tool_calls.append((getattr(func, "__name__", str(func)), func))
                return func

            return decorator

        mock_mcp.tool = mock_tool
        cicd.register_tools(mock_mcp)

        list_func = None
        for name, func in tool_calls:
            if name == "_list_ci_runs":
                list_func = func
                break

        assert list_func is not None

        mock_run = MagicMock()
        mock_run.slug = "run-1"
        mock_run.status = "success"
        mock_run.event_type = "push"
        mock_run.dates = MagicMock()
        mock_run.dates.created_at = "2024-01-15T10:00:00Z"

        mock_result = MagicMock()
        mock_result.runs = [mock_run]

        mock_client.cicd.list_runs = AsyncMock(return_value=mock_result)

        result = await list_func("test", "test-repo", ctx=mock_context)
        assert "CI/CD runs" in result

    @pytest.mark.asyncio
    async def test_register_tools_get_ci_run(self, mock_client) -> None:
        """Test that register_tools registers _get_ci_run."""
        mock_mcp = MagicMock()
        mock_context = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_client

        tool_calls: list[tuple[str, object]] = []

        def mock_tool(**kwargs: object) -> object:
            def decorator(func: object) -> object:
                tool_calls.append((getattr(func, "__name__", str(func)), func))
                return func

            return decorator

        mock_mcp.tool = mock_tool
        cicd.register_tools(mock_mcp)

        get_func = None
        for name, func in tool_calls:
            if name == "_get_ci_run":
                get_func = func
                break

        assert get_func is not None

        mock_run = MagicMock()
        mock_run.slug = "run-123"
        mock_run.status = "success"
        mock_run.event_type = "push"
        mock_run.dates = None
        mock_run.user = None
        mock_run.pull = None
        mock_run.workflows = []
        mock_run.error_messages = []

        mock_client.cicd.get_run = AsyncMock(return_value=mock_run)

        result = await get_func("test", "test-repo", "run-123", ctx=mock_context)
        assert "CI Run #run-123" in result

    @pytest.mark.asyncio
    async def test_register_tools_get_workflow(self, mock_client) -> None:
        """Test that register_tools registers _get_workflow."""
        mock_mcp = MagicMock()
        mock_context = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_client

        tool_calls: list[tuple[str, object]] = []

        def mock_tool(**kwargs: object) -> object:
            def decorator(func: object) -> object:
                tool_calls.append((getattr(func, "__name__", str(func)), func))
                return func

            return decorator

        mock_mcp.tool = mock_tool
        cicd.register_tools(mock_mcp)

        get_func = None
        for name, func in tool_calls:
            if name == "_get_workflow":
                get_func = func
                break

        assert get_func is not None

        mock_workflow = MagicMock()
        mock_workflow.slug = "build"
        mock_workflow.status = "success"
        mock_workflow.description = None
        mock_workflow.dates = None
        mock_workflow.progress = None
        mock_workflow.tasks = []

        mock_client.cicd.get_workflow = AsyncMock(return_value=mock_workflow)

        result = await get_func("test", "test-repo", "run-123", "build", ctx=mock_context)
        assert "Workflow: build" in result

    @pytest.mark.asyncio
    async def test_register_tools_get_cube_logs(self, mock_client) -> None:
        """Test that register_tools registers _get_cube_logs."""
        mock_mcp = MagicMock()
        mock_context = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_client

        tool_calls: list[tuple[str, object]] = []

        def mock_tool(**kwargs: object) -> object:
            def decorator(func: object) -> object:
                tool_calls.append((getattr(func, "__name__", str(func)), func))
                return func

            return decorator

        mock_mcp.tool = mock_tool
        cicd.register_tools(mock_mcp)

        logs_func = None
        for name, func in tool_calls:
            if name == "_get_cube_logs":
                logs_func = func
                break

        assert logs_func is not None

        mock_result = MagicMock()
        mock_result.logs = "test log"
        mock_result.page_complete = False
        mock_result.done = False

        mock_client.cicd.get_cube_logs = AsyncMock(return_value=mock_result)

        result = await logs_func(
            "test", "test-repo", "run-123", "build", "task", "cube", page=1, ctx=mock_context
        )
        assert "Logs for cube" in result

    @pytest.mark.asyncio
    async def test_register_tools_get_artifacts(self, mock_client) -> None:
        """Test that register_tools registers _get_artifacts."""
        mock_mcp = MagicMock()
        mock_context = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_client

        tool_calls: list[tuple[str, object]] = []

        def mock_tool(**kwargs: object) -> object:
            def decorator(func: object) -> object:
                tool_calls.append((getattr(func, "__name__", str(func)), func))
                return func

            return decorator

        mock_mcp.tool = mock_tool
        cicd.register_tools(mock_mcp)

        artifacts_func = None
        for name, func in tool_calls:
            if name == "_get_artifacts":
                artifacts_func = func
                break

        assert artifacts_func is not None

        mock_result = MagicMock()
        mock_result.artifacts = []

        mock_client.cicd.get_artifacts = AsyncMock(return_value=mock_result)

        result = await artifacts_func(
            "test", "test-repo", "run-123", "build", "task", "cube", ctx=mock_context
        )
        assert "No artifacts found" in result

    @pytest.mark.asyncio
    async def test_register_tools_trigger_workflows(self, mock_client) -> None:
        """Test that register_tools registers _trigger_workflows."""
        mock_mcp = MagicMock()
        mock_context = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_client

        tool_calls: list[tuple[str, object]] = []

        def mock_tool(**kwargs: object) -> object:
            def decorator(func: object) -> object:
                tool_calls.append((getattr(func, "__name__", str(func)), func))
                return func

            return decorator

        mock_mcp.tool = mock_tool
        cicd.register_tools(mock_mcp)

        trigger_func = None
        for name, func in tool_calls:
            if name == "_trigger_workflows":
                trigger_func = func
                break

        assert trigger_func is not None

        mock_result = MagicMock()
        mock_result.slug = "12"
        mock_result.status = "created"

        mock_client.cicd.run_workflows = AsyncMock(return_value=mock_result)

        result = await trigger_func(
            "test", "test-repo", ["build"], branch="main", tag="", commit="", ctx=mock_context
        )
        assert "Run triggered successfully" in result
