"""Tests for user tools."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from sourcecraft_mcp.tools import users


class TestGetCurrentUser:
    """Test get_current_user tool."""

    @pytest.mark.asyncio
    async def test_get_current_user_success(self, mock_client, mock_context):
        """Test successful current user retrieval."""
        mock_user = MagicMock()
        mock_user.display_name = "Test User"
        mock_user.username = "testuser"
        mock_user.bio = "A test bio"
        mock_user.location = MagicMock(city="San Francisco", country="USA")
        mock_user.workplace = MagicMock(company="TestCorp", position="Developer")
        mock_user.links = [MagicMock(), MagicMock()]
        mock_user.visibility = "public"

        mock_client.users.get_current = AsyncMock(return_value=mock_user)

        result = await users.get_current_user(ctx=mock_context)

        assert "Test User" in result
        assert "@testuser" in result
        assert "A test bio" in result
        assert "San Francisco" in result
        assert "TestCorp" in result
        assert "Links: 2" in result
        assert "public" in result

    @pytest.mark.asyncio
    async def test_get_current_user_minimal(self, mock_client, mock_context):
        """Test current user with minimal info."""
        mock_user = MagicMock()
        mock_user.display_name = None
        mock_user.username = "testuser"
        mock_user.bio = None
        mock_user.location = MagicMock(city=None, country=None)
        mock_user.workplace = MagicMock(company=None, position=None)
        mock_user.links = []
        mock_user.visibility = "private"

        mock_client.users.get_current = AsyncMock(return_value=mock_user)

        result = await users.get_current_user(ctx=mock_context)

        assert "testuser" in result
        assert "private" in result

    @pytest.mark.asyncio
    async def test_get_current_user_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.users.get_current = AsyncMock(side_effect=Exception("API Error"))

        result = await users.get_current_user(ctx=mock_context)

        assert "Error getting current user" in result


class TestGetUser:
    """Test get_user tool."""

    @pytest.mark.asyncio
    async def test_get_user_success(self, mock_client, mock_context):
        """Test successful user retrieval."""
        mock_user = MagicMock()
        mock_user.display_name = "John Doe"
        mock_user.username = "johndoe"
        mock_user.bio = "Software engineer"
        mock_user.location = MagicMock(city="New York", country="USA")
        mock_user.workplace = MagicMock(company="TechCorp", position="Senior Dev")

        mock_client.users.get = AsyncMock(return_value=mock_user)

        result = await users.get_user(username="johndoe", ctx=mock_context)

        assert "John Doe" in result
        assert "@johndoe" in result
        assert "Software engineer" in result
        assert "New York" in result
        assert "TechCorp" in result

    @pytest.mark.asyncio
    async def test_get_user_no_optional_fields(self, mock_client, mock_context):
        """Test user without optional fields."""
        mock_user = MagicMock()
        mock_user.display_name = None
        mock_user.username = "simpleuser"
        mock_user.bio = None
        mock_user.location = None
        mock_user.workplace = None

        mock_client.users.get = AsyncMock(return_value=mock_user)

        result = await users.get_user(username="simpleuser", ctx=mock_context)

        assert "simpleuser" in result
        assert "@simpleuser" in result

    @pytest.mark.asyncio
    async def test_get_user_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.users.get = AsyncMock(side_effect=Exception("API Error"))

        result = await users.get_user(username="unknown", ctx=mock_context)

        assert "Error getting user" in result


class TestListMyIssues:
    """Test list_my_issues tool."""

    @pytest.mark.asyncio
    async def test_list_my_issues_success(self, mock_client, mock_context):
        """Test successful issue listing."""
        mock_issue1 = MagicMock()
        mock_issue1.slug = "123"
        mock_issue1.title = "Bug fix"
        mock_issue1.status = MagicMock(slug="open", name="Open")
        mock_issue1.priority = "critical"

        mock_issue2 = MagicMock()
        mock_issue2.slug = "124"
        mock_issue2.title = "Feature request"
        mock_issue2.status = MagicMock(slug="closed", name="Closed")
        mock_issue2.priority = "normal"

        mock_result = MagicMock()
        mock_result.issues = [mock_issue1, mock_issue2]

        mock_client.users.list_my_issues = AsyncMock(return_value=mock_result)

        result = await users.list_my_issues(ctx=mock_context)

        assert "Your issues (2)" in result
        assert "Bug fix" in result
        assert "Feature request" in result
        assert "critical" in result

    @pytest.mark.asyncio
    async def test_list_my_issues_empty(self, mock_client, mock_context):
        """Test listing with no issues."""
        mock_result = MagicMock()
        mock_result.issues = []

        mock_client.users.list_my_issues = AsyncMock(return_value=mock_result)

        result = await users.list_my_issues(ctx=mock_context)

        assert "No issues found for you" in result

    @pytest.mark.asyncio
    async def test_list_my_issues_all_priorities(self, mock_client, mock_context):
        """Test listing with all priority types."""
        priorities = ["trivial", "minor", "normal", "critical", "blocker"]
        mock_issues = []

        for i, priority in enumerate(priorities):
            mock_issue = MagicMock()
            mock_issue.slug = f"issue-{i}"
            mock_issue.title = f"{priority.title()} Task"
            mock_issue.status = MagicMock(slug="open", name="Open")
            mock_issue.priority = priority
            mock_issues.append(mock_issue)

        mock_result = MagicMock()
        mock_result.issues = mock_issues

        mock_client.users.list_my_issues = AsyncMock(return_value=mock_result)

        result = await users.list_my_issues(ctx=mock_context)

        for priority in priorities:
            assert f"{priority.title()} Task" in result

    @pytest.mark.asyncio
    async def test_list_my_issues_with_pagination(self, mock_client, mock_context):
        """Test listing with pagination parameters."""
        mock_result = MagicMock()
        mock_result.issues = []

        mock_client.users.list_my_issues = AsyncMock(return_value=mock_result)

        await users.list_my_issues(
            page_size=50,
            page_token="next_page_token",
            ctx=mock_context,
        )

        mock_client.users.list_my_issues.assert_called_once_with(
            page_size=50,
            page_token="next_page_token",
        )

    @pytest.mark.asyncio
    async def test_list_my_issues_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.users.list_my_issues = AsyncMock(side_effect=Exception("API Error"))

        result = await users.list_my_issues(ctx=mock_context)

        assert "Error listing my issues" in result


class TestListUserPullRequests:
    """Test list_user_pull_requests tool."""

    @pytest.mark.asyncio
    async def test_list_user_prs_success(self, mock_client, mock_context):
        """Test successful PR listing."""
        mock_pr1 = MagicMock()
        mock_pr1.slug = "101"
        mock_pr1.title = "Fix bug"
        mock_pr1.source_branch = "feature/bug-fix"
        mock_pr1.target_branch = "main"
        mock_pr1.status = "open"

        mock_pr2 = MagicMock()
        mock_pr2.slug = "102"
        mock_pr2.title = "Add feature"
        mock_pr2.source_branch = "feature/new-thing"
        mock_pr2.target_branch = "develop"
        mock_pr2.status = "merged"

        mock_result = MagicMock()
        mock_result.pull_requests = [mock_pr1, mock_pr2]

        mock_client.users.list_pull_requests = AsyncMock(return_value=mock_result)

        result = await users.list_user_pull_requests(
            username="testuser",
            ctx=mock_context,
        )

        assert "Pull requests for @testuser" in result
        assert "Fix bug" in result
        assert "Add feature" in result
        assert "feature/bug-fix" in result
        assert "merged" in result

    @pytest.mark.asyncio
    async def test_list_user_prs_empty(self, mock_client, mock_context):
        """Test listing with no PRs."""
        mock_result = MagicMock()
        mock_result.pull_requests = []

        mock_client.users.list_pull_requests = AsyncMock(return_value=mock_result)

        result = await users.list_user_pull_requests(
            username="testuser",
            ctx=mock_context,
        )

        assert "No pull requests found for @testuser" in result

    @pytest.mark.asyncio
    async def test_list_user_prs_all_statuses(self, mock_client, mock_context):
        """Test listing with all PR statuses."""
        statuses = ["draft", "open", "discarded", "merging", "merged"]
        mock_prs = []

        for i, status in enumerate(statuses):
            mock_pr = MagicMock()
            mock_pr.slug = f"pr-{i}"
            mock_pr.title = f"{status.title()} PR"
            mock_pr.source_branch = f"branch-{i}"
            mock_pr.target_branch = "main"
            mock_pr.status = status
            mock_prs.append(mock_pr)

        mock_result = MagicMock()
        mock_result.pull_requests = mock_prs

        mock_client.users.list_pull_requests = AsyncMock(return_value=mock_result)

        result = await users.list_user_pull_requests(
            username="testuser",
            ctx=mock_context,
        )

        for status in statuses:
            assert f"{status.title()} PR" in result

    @pytest.mark.asyncio
    async def test_list_user_prs_with_role(self, mock_client, mock_context):
        """Test listing with role filter."""
        mock_pr = MagicMock()
        mock_pr.slug = "101"
        mock_pr.title = "Review PR"
        mock_pr.source_branch = "feature"
        mock_pr.target_branch = "main"
        mock_pr.status = "open"

        mock_result = MagicMock()
        mock_result.pull_requests = [mock_pr]

        mock_client.users.list_pull_requests = AsyncMock(return_value=mock_result)

        result = await users.list_user_pull_requests(
            username="reviewer",
            role="reviewer",
            page_size=20,
            ctx=mock_context,
        )

        assert "role: reviewer" in result
        mock_client.users.list_pull_requests.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_user_prs_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.users.list_pull_requests = AsyncMock(side_effect=Exception("API Error"))

        result = await users.list_user_pull_requests(
            username="testuser",
            ctx=mock_context,
        )

        assert "Error listing user pull requests" in result


class TestRegisterTools:
    """Test register_tools function."""

    @pytest.mark.asyncio
    async def test_register_tools_get_current_user(self, mock_client, mock_context):
        """Test that _get_current_user tool is registered and works."""
        mcp = MagicMock()
        tools = {}

        def mock_tool():
            def decorator(func):
                tools[func.__name__] = func
                return func

            return decorator

        mcp.tool = mock_tool

        users.register_tools(mcp)

        # Test _get_current_user tool
        mock_user = MagicMock()
        mock_user.display_name = "Test User"
        mock_user.username = "testuser"
        mock_user.bio = None
        mock_user.location = None
        mock_user.workplace = None
        mock_user.links = []
        mock_user.visibility = "public"

        mock_client.users.get_current = AsyncMock(return_value=mock_user)

        result = await tools["_get_current_user"](ctx=mock_context)

        assert "Test User" in result
        assert "@testuser" in result

    @pytest.mark.asyncio
    async def test_register_tools_get_user(self, mock_client, mock_context):
        """Test that _get_user tool is registered and works."""
        mcp = MagicMock()
        tools = {}

        def mock_tool():
            def decorator(func):
                tools[func.__name__] = func
                return func

            return decorator

        mcp.tool = mock_tool

        users.register_tools(mcp)

        # Test _get_user tool
        mock_user = MagicMock()
        mock_user.display_name = "John Doe"
        mock_user.username = "johndoe"
        mock_user.bio = None
        mock_user.location = None
        mock_user.workplace = None

        mock_client.users.get = AsyncMock(return_value=mock_user)

        result = await tools["_get_user"](username="johndoe", ctx=mock_context)

        assert "John Doe" in result
        assert "@johndoe" in result

    @pytest.mark.asyncio
    async def test_register_tools_list_my_issues(self, mock_client, mock_context):
        """Test that _list_my_issues tool is registered and works."""
        mcp = MagicMock()
        tools = {}

        def mock_tool():
            def decorator(func):
                tools[func.__name__] = func
                return func

            return decorator

        mcp.tool = mock_tool

        users.register_tools(mcp)

        # Test _list_my_issues tool
        mock_result = MagicMock()
        mock_result.issues = []

        mock_client.users.list_my_issues = AsyncMock(return_value=mock_result)

        result = await tools["_list_my_issues"](
            page_size=30,
            page_token="",
            ctx=mock_context,
        )

        assert "No issues found for you" in result

    @pytest.mark.asyncio
    async def test_register_tools_list_user_pull_requests(self, mock_client, mock_context):
        """Test that _list_user_pull_requests tool is registered and works."""
        mcp = MagicMock()
        tools = {}

        def mock_tool():
            def decorator(func):
                tools[func.__name__] = func
                return func

            return decorator

        mcp.tool = mock_tool

        users.register_tools(mcp)

        # Test _list_user_pull_requests tool
        mock_result = MagicMock()
        mock_result.pull_requests = []

        mock_client.users.list_pull_requests = AsyncMock(return_value=mock_result)

        result = await tools["_list_user_pull_requests"](
            username="testuser",
            role="any",
            page_size=30,
            page_token="",
            ctx=mock_context,
        )

        assert "No pull requests found for @testuser" in result

    def test_register_tools_registers_all_tools(self):
        """Test that all four tools are registered."""
        mcp = MagicMock()
        registered_tools = []

        def mock_tool():
            def decorator(func):
                registered_tools.append(func.__name__)
                return func

            return decorator

        mcp.tool = mock_tool

        users.register_tools(mcp)

        assert "_get_current_user" in registered_tools
        assert "_get_user" in registered_tools
        assert "_list_my_issues" in registered_tools
        assert "_list_user_pull_requests" in registered_tools
        assert len(registered_tools) == 4
