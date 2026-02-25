"""Tests for issue tools."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from sourcecraft_mcp.tools import issues


class TestListIssues:
    """Test list_issues tool."""

    @pytest.mark.asyncio
    async def test_list_issues_success(self, mock_client, mock_context):
        """Test successful issue listing."""
        mock_issue = MagicMock()
        mock_issue.slug = "issue-123"
        mock_issue.title = "Test Issue"
        mock_issue.status = MagicMock(slug="open", name="Open")
        mock_issue.priority = "normal"
        mock_issue.assignee = MagicMock(slug="testuser")

        mock_result = MagicMock()
        mock_result.data = [mock_issue]

        mock_client.issues.list = AsyncMock(return_value=mock_result)

        result = await issues.list_issues(
            owner="test",
            repo="test-repo",
            ctx=mock_context,
        )

        assert "Test Issue" in result
        assert "issue-123" in result
        assert "testuser" in result
        mock_client.issues.list.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_issues_empty(self, mock_client, mock_context):
        """Test listing with no issues."""
        mock_result = MagicMock()
        mock_result.data = []

        mock_client.issues.list = AsyncMock(return_value=mock_result)

        result = await issues.list_issues(
            owner="test",
            repo="test-repo",
            ctx=mock_context,
        )

        assert "No issues found" in result

    @pytest.mark.asyncio
    async def test_list_issues_with_filters(self, mock_client, mock_context):
        """Test listing with status and assignee filters."""
        mock_issue = MagicMock()
        mock_issue.slug = "issue-123"
        mock_issue.title = "Test Issue"
        mock_issue.status = MagicMock(slug="closed", name="Closed")
        mock_issue.priority = "critical"
        mock_issue.assignee = MagicMock(slug="testuser")

        mock_result = MagicMock()
        mock_result.data = [mock_issue]

        mock_client.issues.list = AsyncMock(return_value=mock_result)

        result = await issues.list_issues(
            owner="test",
            repo="test-repo",
            status="closed",
            assignee="testuser",
            label="bug",
            ctx=mock_context,
        )

        assert "Test Issue" in result
        mock_client.issues.list.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_issues_different_statuses(self, mock_client, mock_context):
        """Test listing with different issue statuses."""
        mock_open = MagicMock()
        mock_open.slug = "open-123"
        mock_open.title = "Open Issue"
        mock_open.status = MagicMock(slug="open", name="Open")
        mock_open.priority = "normal"
        mock_open.assignee = None

        mock_closed = MagicMock()
        mock_closed.slug = "closed-123"
        mock_closed.title = "Closed Issue"
        mock_closed.status = MagicMock(slug="closed", name="Closed")
        mock_closed.priority = "normal"
        mock_closed.assignee = None

        mock_other = MagicMock()
        mock_other.slug = "other-123"
        mock_other.title = "Other Issue"
        mock_other.status = MagicMock(slug="inProgress", name="In Progress")
        mock_other.priority = "normal"
        mock_other.assignee = None

        mock_result = MagicMock()
        mock_result.data = [mock_open, mock_closed, mock_other]

        mock_client.issues.list = AsyncMock(return_value=mock_result)

        result = await issues.list_issues(
            owner="test",
            repo="test-repo",
            ctx=mock_context,
        )

        assert "Open Issue" in result
        assert "Closed Issue" in result
        assert "Other Issue" in result

    @pytest.mark.asyncio
    async def test_list_issues_all_priorities(self, mock_client, mock_context):
        """Test listing with all priority types."""
        priorities = ["trivial", "minor", "normal", "critical", "blocker"]
        mock_issues = []

        for i, priority in enumerate(priorities):
            mock_issue = MagicMock()
            mock_issue.slug = f"issue-{i}"
            mock_issue.title = f"{priority.title()} Issue"
            mock_issue.status = MagicMock(slug="open", name="Open")
            mock_issue.priority = priority
            mock_issue.assignee = None
            mock_issues.append(mock_issue)

        mock_result = MagicMock()
        mock_result.data = mock_issues

        mock_client.issues.list = AsyncMock(return_value=mock_result)

        result = await issues.list_issues(
            owner="test",
            repo="test-repo",
            ctx=mock_context,
        )

        for priority in priorities:
            assert f"{priority.title()} Issue" in result

    @pytest.mark.asyncio
    async def test_list_issues_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.issues.list = AsyncMock(side_effect=Exception("API Error"))

        result = await issues.list_issues(
            owner="test",
            repo="test-repo",
            ctx=mock_context,
        )

        assert "Error listing issues" in result


class TestGetIssue:
    """Test get_issue tool."""

    @pytest.mark.asyncio
    async def test_get_issue_success(self, mock_client, mock_context):
        """Test successful issue retrieval."""
        mock_issue = MagicMock()
        mock_issue.slug = "123"
        mock_issue.title = "Test Issue"
        mock_issue.description = "Test description"
        mock_issue.status = MagicMock(slug="open", name="Open")
        mock_issue.priority = "normal"
        mock_issue.author = MagicMock(slug="authoruser")
        mock_issue.assignee = MagicMock(slug="assigneeuser")
        bug_label = MagicMock()
        bug_label.name = "bug"
        urgent_label = MagicMock()
        urgent_label.name = "urgent"
        mock_issue.labels = [bug_label, urgent_label]
        mock_issue.milestone = MagicMock(slug="v1.0")
        mock_issue.deadline = "2024-12-31"
        mock_issue.linked_prs = [MagicMock(slug="456")]
        mock_issue.created_at = "2024-01-01"
        mock_issue.updated_at = "2024-01-02"

        mock_client.issues.get = AsyncMock(return_value=mock_issue)

        result = await issues.get_issue(
            owner="test",
            repo="test-repo",
            issue_number=123,
            ctx=mock_context,
        )

        assert "Test Issue" in result
        assert "Test description" in result
        assert "authoruser" in result
        assert "assigneeuser" in result
        assert "bug" in result
        assert "v1.0" in result
        assert "2024-12-31" in result
        assert "#456" in result

    @pytest.mark.asyncio
    async def test_get_issue_no_optional_fields(self, mock_client, mock_context):
        """Test issue without optional fields."""
        mock_issue = MagicMock()
        mock_issue.slug = "123"
        mock_issue.title = "Simple Issue"
        mock_issue.description = None
        mock_issue.status = MagicMock(slug="open", name="Open")
        mock_issue.priority = None
        mock_issue.author = None
        mock_issue.assignee = None
        mock_issue.labels = []
        mock_issue.milestone = None
        mock_issue.deadline = None
        mock_issue.linked_prs = []
        mock_issue.created_at = "2024-01-01"
        mock_issue.updated_at = "2024-01-01"

        mock_client.issues.get = AsyncMock(return_value=mock_issue)

        result = await issues.get_issue(
            owner="test",
            repo="test-repo",
            issue_number=123,
            ctx=mock_context,
        )

        assert "Simple Issue" in result
        assert "No description" in result
        assert "normal" in result
        assert "unknown" in result

    @pytest.mark.asyncio
    async def test_get_issue_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.issues.get = AsyncMock(side_effect=Exception("API Error"))

        result = await issues.get_issue(
            owner="test",
            repo="test-repo",
            issue_number=123,
            ctx=mock_context,
        )

        assert "Error getting issue" in result


class TestCreateIssue:
    """Test create_issue tool."""

    @pytest.mark.asyncio
    async def test_create_issue_success(self, mock_client, mock_context):
        """Test successful issue creation."""
        mock_issue = MagicMock()
        mock_issue.slug = "456"
        mock_issue.title = "New Issue"
        mock_issue.status = MagicMock(name="Open")
        mock_issue.priority = "normal"
        mock_issue.author = MagicMock(slug="creator")

        mock_client.issues.create = AsyncMock(return_value=mock_issue)

        result = await issues.create_issue(
            owner="test",
            repo="test-repo",
            title="New Issue",
            description="Issue description",
            priority="normal",
            ctx=mock_context,
        )

        assert "Issue created successfully" in result
        assert "New Issue" in result
        assert "456" in result
        mock_client.issues.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_issue_with_assignee_and_labels(self, mock_client, mock_context):
        """Test creation with assignee and labels."""
        mock_issue = MagicMock()
        mock_issue.slug = "789"
        mock_issue.title = "Labeled Issue"
        mock_issue.status = MagicMock(name="Open")
        mock_issue.priority = "critical"
        mock_issue.author = MagicMock(slug="creator")

        mock_client.issues.create = AsyncMock(return_value=mock_issue)

        result = await issues.create_issue(
            owner="test",
            repo="test-repo",
            title="Labeled Issue",
            description="Issue description",
            priority="critical",
            assignee_id="testuser",
            label_slugs=["bug", "urgent"],
            ctx=mock_context,
        )

        assert "Issue created successfully" in result

    @pytest.mark.asyncio
    async def test_create_issue_minimal(self, mock_client, mock_context):
        """Test creation with minimal fields."""
        mock_issue = MagicMock()
        mock_issue.slug = "101"
        mock_issue.title = "Minimal Issue"
        mock_issue.status = MagicMock(name="Open")
        mock_issue.priority = None
        mock_issue.author = None

        mock_client.issues.create = AsyncMock(return_value=mock_issue)

        result = await issues.create_issue(
            owner="test",
            repo="test-repo",
            title="Minimal Issue",
            ctx=mock_context,
        )

        assert "Issue created successfully" in result
        assert "Minimal Issue" in result

    @pytest.mark.asyncio
    async def test_create_issue_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.issues.create = AsyncMock(side_effect=Exception("API Error"))

        result = await issues.create_issue(
            owner="test",
            repo="test-repo",
            title="New Issue",
            ctx=mock_context,
        )

        assert "Error creating issue" in result


class TestUpdateIssue:
    """Test update_issue tool."""

    @pytest.mark.asyncio
    async def test_update_issue_success(self, mock_client, mock_context):
        """Test successful issue update."""
        mock_issue = MagicMock()
        mock_issue.slug = "123"
        mock_issue.title = "Updated Issue"
        mock_issue.status = MagicMock(name="In Progress")
        mock_issue.priority = "high"

        mock_client.issues.update = AsyncMock(return_value=mock_issue)

        result = await issues.update_issue(
            owner="test",
            repo="test-repo",
            issue_number=123,
            title="Updated Issue",
            description="Updated description",
            status_slug="inProgress",
            priority="high",
            assignee_id="newuser",
            ctx=mock_context,
        )

        assert "Issue updated successfully" in result
        assert "Updated Issue" in result
        mock_client.issues.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_issue_partial(self, mock_client, mock_context):
        """Test partial update (only title)."""
        mock_issue = MagicMock()
        mock_issue.slug = "123"
        mock_issue.title = "New Title"
        mock_issue.status = MagicMock(name="Open")
        mock_issue.priority = "normal"

        mock_client.issues.update = AsyncMock(return_value=mock_issue)

        result = await issues.update_issue(
            owner="test",
            repo="test-repo",
            issue_number=123,
            title="New Title",
            ctx=mock_context,
        )

        assert "Issue updated successfully" in result
        assert "New Title" in result

    @pytest.mark.asyncio
    async def test_update_issue_unassign(self, mock_client, mock_context):
        """Test unassigning issue."""
        mock_issue = MagicMock()
        mock_issue.slug = "123"
        mock_issue.title = "Issue"
        mock_issue.status = MagicMock(name="Open")
        mock_issue.priority = "normal"

        mock_client.issues.update = AsyncMock(return_value=mock_issue)

        result = await issues.update_issue(
            owner="test",
            repo="test-repo",
            issue_number=123,
            assignee_id="",
            ctx=mock_context,
        )

        assert "Issue updated successfully" in result

    @pytest.mark.asyncio
    async def test_update_issue_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.issues.update = AsyncMock(side_effect=Exception("API Error"))

        result = await issues.update_issue(
            owner="test",
            repo="test-repo",
            issue_number=123,
            title="Updated Issue",
            ctx=mock_context,
        )

        assert "Error updating issue" in result


class TestCloseIssue:
    """Test close_issue tool."""

    @pytest.mark.asyncio
    async def test_close_issue_success(self, mock_client, mock_context):
        """Test successful issue closing."""
        mock_client.issues.close = AsyncMock(return_value=None)

        result = await issues.close_issue(
            owner="test",
            repo="test-repo",
            issue_number=123,
            ctx=mock_context,
        )

        assert "Issue #123 in 'test/test-repo' closed successfully" in result
        mock_client.issues.close.assert_called_once_with(
            owner="test",
            repo="test-repo",
            issue_number=123,
        )

    @pytest.mark.asyncio
    async def test_close_issue_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.issues.close = AsyncMock(side_effect=Exception("API Error"))

        result = await issues.close_issue(
            owner="test",
            repo="test-repo",
            issue_number=123,
            ctx=mock_context,
        )

        assert "Error closing issue" in result


class TestReopenIssue:
    """Test reopen_issue tool."""

    @pytest.mark.asyncio
    async def test_reopen_issue_success(self, mock_client, mock_context):
        """Test successful issue reopening."""
        mock_client.issues.reopen = AsyncMock(return_value=None)

        result = await issues.reopen_issue(
            owner="test",
            repo="test-repo",
            issue_number=123,
            ctx=mock_context,
        )

        assert "Issue #123 in 'test/test-repo' reopened successfully" in result
        mock_client.issues.reopen.assert_called_once_with(
            owner="test",
            repo="test-repo",
            issue_number=123,
        )

    @pytest.mark.asyncio
    async def test_reopen_issue_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.issues.reopen = AsyncMock(side_effect=Exception("API Error"))

        result = await issues.reopen_issue(
            owner="test",
            repo="test-repo",
            issue_number=123,
            ctx=mock_context,
        )

        assert "Error reopening issue" in result


class TestListIssueComments:
    """Test list_issue_comments tool."""

    @pytest.mark.asyncio
    async def test_list_comments_success(self, mock_client, mock_context):
        """Test successful comment listing."""
        mock_comment = MagicMock()
        mock_comment.author = MagicMock(slug="testuser")
        mock_comment.created_at = "2024-01-15 10:00"
        mock_comment.body = "This is a test comment"

        mock_result = MagicMock()
        mock_result.data = [mock_comment]

        mock_client.issues.list_comments = AsyncMock(return_value=mock_result)

        result = await issues.list_issue_comments(
            owner="test",
            repo="test-repo",
            issue_number=123,
            ctx=mock_context,
        )

        assert "Comments on issue #123" in result
        assert "testuser" in result
        assert "This is a test comment" in result
        mock_client.issues.list_comments.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_comments_empty(self, mock_client, mock_context):
        """Test listing with no comments."""
        mock_result = MagicMock()
        mock_result.data = []

        mock_client.issues.list_comments = AsyncMock(return_value=mock_result)

        result = await issues.list_issue_comments(
            owner="test",
            repo="test-repo",
            issue_number=123,
            ctx=mock_context,
        )

        assert "No comments on issue #123" in result

    @pytest.mark.asyncio
    async def test_list_comments_no_author(self, mock_client, mock_context):
        """Test comment without author."""
        mock_comment = MagicMock()
        mock_comment.author = None
        mock_comment.created_at = "2024-01-15 10:00"
        mock_comment.body = "Anonymous comment"

        mock_result = MagicMock()
        mock_result.data = [mock_comment]

        mock_client.issues.list_comments = AsyncMock(return_value=mock_result)

        result = await issues.list_issue_comments(
            owner="test",
            repo="test-repo",
            issue_number=123,
            ctx=mock_context,
        )

        assert "unknown" in result
        assert "Anonymous comment" in result

    @pytest.mark.asyncio
    async def test_list_comments_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.issues.list_comments = AsyncMock(side_effect=Exception("API Error"))

        result = await issues.list_issue_comments(
            owner="test",
            repo="test-repo",
            issue_number=123,
            ctx=mock_context,
        )

        assert "Error listing comments" in result


class TestAddIssueComment:
    """Test add_issue_comment tool."""

    @pytest.mark.asyncio
    async def test_add_comment_success(self, mock_client, mock_context):
        """Test successful comment addition."""
        mock_comment = MagicMock()
        mock_comment.author = MagicMock(slug="commenter")

        mock_client.issues.create_comment = AsyncMock(return_value=mock_comment)

        result = await issues.add_issue_comment(
            owner="test",
            repo="test-repo",
            issue_number=123,
            body="This is a new comment",
            ctx=mock_context,
        )

        assert "Comment added to issue #123 by @commenter" in result
        mock_client.issues.create_comment.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_comment_no_author(self, mock_client, mock_context):
        """Test comment without author info."""
        mock_comment = MagicMock()
        mock_comment.author = None

        mock_client.issues.create_comment = AsyncMock(return_value=mock_comment)

        result = await issues.add_issue_comment(
            owner="test",
            repo="test-repo",
            issue_number=123,
            body="Test comment",
            ctx=mock_context,
        )

        assert "Comment added to issue #123 by @unknown" in result

    @pytest.mark.asyncio
    async def test_add_comment_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.issues.create_comment = AsyncMock(side_effect=Exception("API Error"))

        result = await issues.add_issue_comment(
            owner="test",
            repo="test-repo",
            issue_number=123,
            body="Test comment",
            ctx=mock_context,
        )

        assert "Error adding comment" in result


class TestRegisterTools:
    """Test register_tools function."""

    def test_register_tools_registers_all_tools(self):
        """Test that all tools are registered."""
        mock_mcp = MagicMock()
        tool_count = []

        def capture_tool(func):
            tool_count.append(func.__name__)
            return func

        mock_mcp.tool = MagicMock(return_value=capture_tool)
        issues.register_tools(mock_mcp)

        assert mock_mcp.tool.call_count == 8

    @pytest.mark.asyncio
    async def test_register_tools_list_issues(self):
        """Test that register_tools registers list_issues."""
        mock_mcp = MagicMock()
        mock_client = MagicMock()
        mock_context = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_client

        tool_calls = []

        def mock_tool(**kwargs):
            def decorator(func):
                tool_calls.append((func.__name__, func))
                return func

            return decorator

        mock_mcp.tool = mock_tool
        issues.register_tools(mock_mcp)

        list_func = None
        for name, func in tool_calls:
            if name == "_list_issues":
                list_func = func
                break

        assert list_func is not None

        mock_issue = MagicMock()
        mock_issue.slug = "123"
        mock_issue.title = "Test Issue"
        mock_issue.status = MagicMock(slug="open", name="Open")
        mock_issue.priority = "normal"
        mock_issue.assignee = None

        mock_result = MagicMock()
        mock_result.data = [mock_issue]
        mock_client.issues.list = AsyncMock(return_value=mock_result)

        result = await list_func("test", "test-repo", ctx=mock_context)
        assert "Test Issue" in result

    @pytest.mark.asyncio
    async def test_register_tools_get_issue(self):
        """Test that register_tools registers get_issue."""
        mock_mcp = MagicMock()
        mock_client = MagicMock()
        mock_context = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_client

        tool_calls = []

        def mock_tool(**kwargs):
            def decorator(func):
                tool_calls.append((func.__name__, func))
                return func

            return decorator

        mock_mcp.tool = mock_tool
        issues.register_tools(mock_mcp)

        get_func = None
        for name, func in tool_calls:
            if name == "_get_issue":
                get_func = func
                break

        assert get_func is not None

        mock_issue = MagicMock()
        mock_issue.slug = "123"
        mock_issue.title = "Test Issue"
        mock_issue.description = "Description"
        mock_issue.status = MagicMock(slug="open", name="Open")
        mock_issue.priority = "normal"
        mock_issue.author = MagicMock(slug="author")
        mock_issue.assignee = None
        mock_issue.labels = []
        mock_issue.milestone = None
        mock_issue.deadline = None
        mock_issue.linked_prs = []
        mock_issue.created_at = "2024-01-01"
        mock_issue.updated_at = "2024-01-01"

        mock_client.issues.get = AsyncMock(return_value=mock_issue)

        result = await get_func("test", "test-repo", 123, ctx=mock_context)
        assert "Test Issue" in result

    @pytest.mark.asyncio
    async def test_register_tools_create_issue(self):
        """Test that register_tools registers create_issue."""
        mock_mcp = MagicMock()
        mock_client = MagicMock()
        mock_context = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_client

        tool_calls = []

        def mock_tool(**kwargs):
            def decorator(func):
                tool_calls.append((func.__name__, func))
                return func

            return decorator

        mock_mcp.tool = mock_tool
        issues.register_tools(mock_mcp)

        create_func = None
        for name, func in tool_calls:
            if name == "_create_issue":
                create_func = func
                break

        assert create_func is not None

        mock_issue = MagicMock()
        mock_issue.slug = "456"
        mock_issue.title = "New Issue"
        mock_issue.status = MagicMock(name="Open")
        mock_issue.priority = "normal"

        mock_client.issues.create = AsyncMock(return_value=mock_issue)

        result = await create_func("test", "test-repo", "New Issue", ctx=mock_context)
        assert "Issue created successfully" in result

    @pytest.mark.asyncio
    async def test_register_tools_update_issue(self):
        """Test that register_tools registers update_issue."""
        mock_mcp = MagicMock()
        mock_client = MagicMock()
        mock_context = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_client

        tool_calls = []

        def mock_tool(**kwargs):
            def decorator(func):
                tool_calls.append((func.__name__, func))
                return func

            return decorator

        mock_mcp.tool = mock_tool
        issues.register_tools(mock_mcp)

        update_func = None
        for name, func in tool_calls:
            if name == "_update_issue":
                update_func = func
                break

        assert update_func is not None

        mock_issue = MagicMock()
        mock_issue.slug = "123"
        mock_issue.title = "Updated Issue"
        mock_issue.status = MagicMock(name="Open")
        mock_issue.priority = "normal"

        mock_client.issues.update = AsyncMock(return_value=mock_issue)

        result = await update_func(
            "test", "test-repo", 123, title="Updated Issue", ctx=mock_context
        )
        assert "Issue updated successfully" in result

    @pytest.mark.asyncio
    async def test_register_tools_close_issue(self):
        """Test that register_tools registers close_issue."""
        mock_mcp = MagicMock()
        mock_client = MagicMock()
        mock_context = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_client

        tool_calls = []

        def mock_tool(**kwargs):
            def decorator(func):
                tool_calls.append((func.__name__, func))
                return func

            return decorator

        mock_mcp.tool = mock_tool
        issues.register_tools(mock_mcp)

        close_func = None
        for name, func in tool_calls:
            if name == "_close_issue":
                close_func = func
                break

        assert close_func is not None

        mock_client.issues.close = AsyncMock(return_value=None)

        result = await close_func("test", "test-repo", 123, ctx=mock_context)
        assert "closed successfully" in result

    @pytest.mark.asyncio
    async def test_register_tools_reopen_issue(self):
        """Test that register_tools registers reopen_issue."""
        mock_mcp = MagicMock()
        mock_client = MagicMock()
        mock_context = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_client

        tool_calls = []

        def mock_tool(**kwargs):
            def decorator(func):
                tool_calls.append((func.__name__, func))
                return func

            return decorator

        mock_mcp.tool = mock_tool
        issues.register_tools(mock_mcp)

        reopen_func = None
        for name, func in tool_calls:
            if name == "_reopen_issue":
                reopen_func = func
                break

        assert reopen_func is not None

        mock_client.issues.reopen = AsyncMock(return_value=None)

        result = await reopen_func("test", "test-repo", 123, ctx=mock_context)
        assert "reopened successfully" in result

    @pytest.mark.asyncio
    async def test_register_tools_list_issue_comments(self):
        """Test that register_tools registers list_issue_comments."""
        mock_mcp = MagicMock()
        mock_client = MagicMock()
        mock_context = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_client

        tool_calls = []

        def mock_tool(**kwargs):
            def decorator(func):
                tool_calls.append((func.__name__, func))
                return func

            return decorator

        mock_mcp.tool = mock_tool
        issues.register_tools(mock_mcp)

        list_comments_func = None
        for name, func in tool_calls:
            if name == "_list_issue_comments":
                list_comments_func = func
                break

        assert list_comments_func is not None

        mock_comment = MagicMock()
        mock_comment.author = MagicMock(slug="testuser")
        mock_comment.created_at = "2024-01-15"
        mock_comment.body = "Test comment"

        mock_result = MagicMock()
        mock_result.data = [mock_comment]
        mock_client.issues.list_comments = AsyncMock(return_value=mock_result)

        result = await list_comments_func("test", "test-repo", 123, ctx=mock_context)
        assert "Test comment" in result

    @pytest.mark.asyncio
    async def test_register_tools_add_issue_comment(self):
        """Test that register_tools registers add_issue_comment."""
        mock_mcp = MagicMock()
        mock_client = MagicMock()
        mock_context = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_client

        tool_calls = []

        def mock_tool(**kwargs):
            def decorator(func):
                tool_calls.append((func.__name__, func))
                return func

            return decorator

        mock_mcp.tool = mock_tool
        issues.register_tools(mock_mcp)

        add_comment_func = None
        for name, func in tool_calls:
            if name == "_add_issue_comment":
                add_comment_func = func
                break

        assert add_comment_func is not None

        mock_comment = MagicMock()
        mock_comment.author = MagicMock(slug="commenter")

        mock_client.issues.create_comment = AsyncMock(return_value=mock_comment)

        result = await add_comment_func("test", "test-repo", 123, "New comment", ctx=mock_context)
        assert "Comment added" in result
