"""Tests for pull request tools."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from sourcecraft_mcp.tools import pull_requests


class TestRegisterTools:
    """Test register_tools function."""

    @pytest.mark.asyncio
    async def test_register_tools_list_pull_requests(self):
        """Test that register_tools registers list_pull_requests."""
        mock_mcp = MagicMock()
        mock_client = MagicMock()
        mock_context = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_client

        # Get the tool decorator callback
        tool_calls = []

        def mock_tool(**kwargs):
            def decorator(func):
                tool_calls.append((kwargs.get("name"), func))
                return func

            return decorator

        mock_mcp.tool = mock_tool

        # Register tools
        pull_requests.register_tools(mock_mcp)

        # Find and test list_pull_requests
        list_pr_func = None
        for name, func in tool_calls:
            if "list_pull_requests" in str(func.__name__):
                list_pr_func = func
                break

        assert list_pr_func is not None

        # Mock the return value
        mock_pr = MagicMock()
        mock_pr.slug = "123"
        mock_pr.title = "Test PR"
        mock_pr.status = "open"
        mock_pr.source_branch = "feature"
        mock_pr.target_branch = "main"
        mock_pr.author = MagicMock(slug="testuser")

        mock_result = MagicMock()
        mock_result.data = [mock_pr]
        mock_client.pull_requests.list = AsyncMock(return_value=mock_result)

        result = await list_pr_func("test", "test-repo", ctx=mock_context)
        assert "Test PR" in result

    @pytest.mark.asyncio
    async def test_register_tools_get_pull_request(self):
        """Test that register_tools registers get_pull_request."""
        mock_mcp = MagicMock()
        mock_client = MagicMock()
        mock_context = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_client

        tool_calls = []

        def mock_tool(**kwargs):
            def decorator(func):
                tool_calls.append((kwargs.get("name"), func))
                return func

            return decorator

        mock_mcp.tool = mock_tool
        pull_requests.register_tools(mock_mcp)

        get_pr_func = None
        for name, func in tool_calls:
            if "get_pull_request" in str(func.__name__):
                get_pr_func = func
                break

        assert get_pr_func is not None

        mock_pr = MagicMock()
        mock_pr.slug = "123"
        mock_pr.title = "Test PR"
        mock_pr.status = "open"
        mock_pr.author = MagicMock(slug="author")
        mock_pr.source_branch = "feature"
        mock_pr.target_branch = "main"
        mock_pr.description = None
        mock_pr.merge_info = None
        mock_pr.created_at = "2024-01-01"
        mock_pr.updated_at = "2024-01-01"

        mock_client.pull_requests.get = AsyncMock(return_value=mock_pr)

        result = await get_pr_func("test", "test-repo", 123, ctx=mock_context)
        assert "Test PR" in result

    @pytest.mark.asyncio
    async def test_register_tools_create_pull_request(self):
        """Test that register_tools registers create_pull_request."""
        mock_mcp = MagicMock()
        mock_client = MagicMock()
        mock_context = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_client

        tool_calls = []

        def mock_tool(**kwargs):
            def decorator(func):
                tool_calls.append((kwargs.get("name"), func))
                return func

            return decorator

        mock_mcp.tool = mock_tool
        pull_requests.register_tools(mock_mcp)

        create_pr_func = None
        for name, func in tool_calls:
            if "create_pull_request" in str(func.__name__):
                create_pr_func = func
                break

        assert create_pr_func is not None

        mock_pr = MagicMock()
        mock_pr.slug = "456"
        mock_pr.title = "New PR"
        mock_pr.source_branch = "feature"
        mock_pr.target_branch = "main"
        mock_pr.author = MagicMock(slug="creator")

        mock_client.pull_requests.create = AsyncMock(return_value=mock_pr)

        result = await create_pr_func(
            "test",
            "test-repo",
            "New PR",
            "feature",
            "main",
            description="Test",
            publish=True,
            ctx=mock_context,
        )
        assert "Pull request created" in result

    @pytest.mark.asyncio
    async def test_register_tools_update_pull_request(self):
        """Test that register_tools registers update_pull_request."""
        mock_mcp = MagicMock()
        mock_client = MagicMock()
        mock_context = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_client

        tool_calls = []

        def mock_tool(**kwargs):
            def decorator(func):
                tool_calls.append((kwargs.get("name"), func))
                return func

            return decorator

        mock_mcp.tool = mock_tool
        pull_requests.register_tools(mock_mcp)

        update_pr_func = None
        for name, func in tool_calls:
            if "update_pull_request" in str(func.__name__):
                update_pr_func = func
                break

        assert update_pr_func is not None

        mock_pr = MagicMock()
        mock_pr.slug = "123"
        mock_pr.title = "Updated"

        mock_client.pull_requests.update = AsyncMock(return_value=mock_pr)

        result = await update_pr_func("test", "test-repo", 123, title="Updated", ctx=mock_context)
        assert "Pull request updated" in result

    @pytest.mark.asyncio
    async def test_register_tools_merge_pull_request(self):
        """Test that register_tools registers merge_pull_request."""
        mock_mcp = MagicMock()
        mock_client = MagicMock()
        mock_context = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_client

        tool_calls = []

        def mock_tool(**kwargs):
            def decorator(func):
                tool_calls.append((kwargs.get("name"), func))
                return func

            return decorator

        mock_mcp.tool = mock_tool
        pull_requests.register_tools(mock_mcp)

        merge_pr_func = None
        for name, func in tool_calls:
            if "merge_pull_request" in str(func.__name__):
                merge_pr_func = func
                break

        assert merge_pr_func is not None

        mock_pr = MagicMock()
        mock_pr.merge_info = MagicMock(merge_commit_hash="abc123")

        mock_client.pull_requests.merge = AsyncMock(return_value=mock_pr)

        result = await merge_pr_func("test", "test-repo", 123, ctx=mock_context)
        assert "merged successfully" in result

    @pytest.mark.asyncio
    async def test_register_tools_publish_pull_request(self):
        """Test that register_tools registers publish_pull_request."""
        mock_mcp = MagicMock()
        mock_client = MagicMock()
        mock_context = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_client

        tool_calls = []

        def mock_tool(**kwargs):
            def decorator(func):
                tool_calls.append((kwargs.get("name"), func))
                return func

            return decorator

        mock_mcp.tool = mock_tool
        pull_requests.register_tools(mock_mcp)

        publish_pr_func = None
        for name, func in tool_calls:
            if "publish_pull_request" in str(func.__name__):
                publish_pr_func = func
                break

        assert publish_pr_func is not None

        mock_pr = MagicMock()
        mock_pr.status = "open"

        mock_client.pull_requests.publish = AsyncMock(return_value=mock_pr)

        result = await publish_pr_func("test", "test-repo", 123, ctx=mock_context)
        assert "published" in result

    @pytest.mark.asyncio
    async def test_register_tools_discard_pull_request(self):
        """Test that register_tools registers discard_pull_request."""
        mock_mcp = MagicMock()
        mock_client = MagicMock()
        mock_context = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_client

        tool_calls = []

        def mock_tool(**kwargs):
            def decorator(func):
                tool_calls.append((kwargs.get("name"), func))
                return func

            return decorator

        mock_mcp.tool = mock_tool
        pull_requests.register_tools(mock_mcp)

        discard_pr_func = None
        for name, func in tool_calls:
            if "discard_pull_request" in str(func.__name__):
                discard_pr_func = func
                break

        assert discard_pr_func is not None

        mock_pr = MagicMock()
        mock_pr.status = "discarded"

        mock_client.pull_requests.discard = AsyncMock(return_value=mock_pr)

        result = await discard_pr_func("test", "test-repo", 123, ctx=mock_context)
        assert "discarded" in result

    @pytest.mark.asyncio
    async def test_register_tools_list_pr_reviewers(self):
        """Test that register_tools registers list_pr_reviewers."""
        mock_mcp = MagicMock()
        mock_client = MagicMock()
        mock_context = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_client

        tool_calls = []

        def mock_tool(**kwargs):
            def decorator(func):
                tool_calls.append((kwargs.get("name"), func))
                return func

            return decorator

        mock_mcp.tool = mock_tool
        pull_requests.register_tools(mock_mcp)

        list_reviewers_func = None
        for name, func in tool_calls:
            if "list_pr_reviewers" in str(func.__name__):
                list_reviewers_func = func
                break

        assert list_reviewers_func is not None

        mock_reviewer = MagicMock()
        mock_reviewer.user = MagicMock(slug="reviewer1")
        mock_reviewer.review_decision = "approve"

        mock_result = MagicMock()
        mock_result.reviewers = [mock_reviewer]

        mock_client.pull_requests.list_reviewers = AsyncMock(return_value=mock_result)

        result = await list_reviewers_func("test", "test-repo", 123, ctx=mock_context)
        assert "Reviewers for PR #123" in result

    @pytest.mark.asyncio
    async def test_register_tools_add_pr_reviewer(self):
        """Test that register_tools registers add_pr_reviewer."""
        mock_mcp = MagicMock()
        mock_client = MagicMock()
        mock_context = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_client

        tool_calls = []

        def mock_tool(**kwargs):
            def decorator(func):
                tool_calls.append((kwargs.get("name"), func))
                return func

            return decorator

        mock_mcp.tool = mock_tool
        pull_requests.register_tools(mock_mcp)

        add_reviewer_func = None
        for name, func in tool_calls:
            if "add_pr_reviewer" in str(func.__name__):
                add_reviewer_func = func
                break

        assert add_reviewer_func is not None

        mock_client.pull_requests.add_reviewer = AsyncMock(return_value=None)

        result = await add_reviewer_func("test", "test-repo", 123, "reviewer1", ctx=mock_context)
        assert "Reviewer added" in result

    @pytest.mark.asyncio
    async def test_register_tools_set_review_decision(self):
        """Test that register_tools registers set_review_decision."""
        mock_mcp = MagicMock()
        mock_client = MagicMock()
        mock_context = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_client

        tool_calls = []

        def mock_tool(**kwargs):
            def decorator(func):
                tool_calls.append((kwargs.get("name"), func))
                return func

            return decorator

        mock_mcp.tool = mock_tool
        pull_requests.register_tools(mock_mcp)

        set_decision_func = None
        for name, func in tool_calls:
            if "set_review_decision" in str(func.__name__):
                set_decision_func = func
                break

        assert set_decision_func is not None

        mock_client.pull_requests.set_review_decision = AsyncMock(return_value=None)

        result = await set_decision_func("test", "test-repo", 123, "approve", ctx=mock_context)
        assert "approve" in result

    def test_register_tools_registers_all_tools(self):
        """Test that all tools are registered."""
        mock_mcp = MagicMock()
        tool_count = [0]

        def mock_tool(**kwargs):
            def decorator(func):
                tool_count[0] += 1
                return func

            return decorator

        mock_mcp.tool = mock_tool
        pull_requests.register_tools(mock_mcp)

        assert tool_count[0] == 10  # We have 10 tools


class TestListPullRequests:
    """Test list_pull_requests tool."""

    @pytest.mark.asyncio
    async def test_list_prs_success(self, mock_client, mock_context):
        """Test successful PR listing."""
        mock_pr = MagicMock()
        mock_pr.slug = "123"
        mock_pr.title = "Test PR"
        mock_pr.status = "open"
        mock_pr.source_branch = "feature-branch"
        mock_pr.target_branch = "main"
        mock_pr.author = MagicMock(slug="testuser")

        mock_result = MagicMock()
        mock_result.data = [mock_pr]

        mock_client.pull_requests.list = AsyncMock(return_value=mock_result)

        result = await pull_requests.list_pull_requests(
            owner="test",
            repo="test-repo",
            ctx=mock_context,
        )

        assert "Test PR" in result
        assert "123" in result
        assert "testuser" in result
        assert "feature-branch" in result
        assert "main" in result
        mock_client.pull_requests.list.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_prs_empty(self, mock_client, mock_context):
        """Test listing with no PRs."""
        mock_result = MagicMock()
        mock_result.data = []

        mock_client.pull_requests.list = AsyncMock(return_value=mock_result)

        result = await pull_requests.list_pull_requests(
            owner="test",
            repo="test-repo",
            ctx=mock_context,
        )

        assert "No pull requests found" in result

    @pytest.mark.asyncio
    async def test_list_prs_with_all_filters(self, mock_client, mock_context):
        """Test listing with all filters applied."""
        mock_pr = MagicMock()
        mock_pr.slug = "456"
        mock_pr.title = "Filtered PR"
        mock_pr.status = "draft"
        mock_pr.source_branch = "develop"
        mock_pr.target_branch = "main"
        mock_pr.author = MagicMock(slug="authoruser")

        mock_result = MagicMock()
        mock_result.data = [mock_pr]

        mock_client.pull_requests.list = AsyncMock(return_value=mock_result)

        result = await pull_requests.list_pull_requests(
            owner="test",
            repo="test-repo",
            status="draft",
            author="authoruser",
            source_branch="develop",
            target_branch="main",
            page=2,
            per_page=50,
            ctx=mock_context,
        )

        assert "Filtered PR" in result
        mock_client.pull_requests.list.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_prs_all_statuses(self, mock_client, mock_context):
        """Test listing with all PR statuses."""
        statuses = ["draft", "open", "discarded", "merging", "merged"]
        mock_prs = []

        for i, status in enumerate(statuses):
            mock_pr = MagicMock()
            mock_pr.slug = f"pr-{i}"
            mock_pr.title = f"{status.title()} PR"
            mock_pr.status = status
            mock_pr.source_branch = f"branch-{i}"
            mock_pr.target_branch = "main"
            mock_pr.author = MagicMock(slug=f"user-{i}")
            mock_prs.append(mock_pr)

        mock_result = MagicMock()
        mock_result.data = mock_prs

        mock_client.pull_requests.list = AsyncMock(return_value=mock_result)

        result = await pull_requests.list_pull_requests(
            owner="test",
            repo="test-repo",
            ctx=mock_context,
        )

        for status in statuses:
            assert f"{status.title()} PR" in result

    @pytest.mark.asyncio
    async def test_list_prs_no_author(self, mock_client, mock_context):
        """Test PR without author."""
        mock_pr = MagicMock()
        mock_pr.slug = "789"
        mock_pr.title = "Anonymous PR"
        mock_pr.status = "open"
        mock_pr.source_branch = "feature"
        mock_pr.target_branch = "main"
        mock_pr.author = None

        mock_result = MagicMock()
        mock_result.data = [mock_pr]

        mock_client.pull_requests.list = AsyncMock(return_value=mock_result)

        result = await pull_requests.list_pull_requests(
            owner="test",
            repo="test-repo",
            ctx=mock_context,
        )

        assert "Anonymous PR" in result
        assert "unknown" in result

    @pytest.mark.asyncio
    async def test_list_prs_result_without_data_attr(self, mock_client, mock_context):
        """Test when result doesn't have data attribute."""
        mock_result = []  # Not a MagicMock with data attribute

        mock_client.pull_requests.list = AsyncMock(return_value=mock_result)

        result = await pull_requests.list_pull_requests(
            owner="test",
            repo="test-repo",
            ctx=mock_context,
        )

        assert "No pull requests found" in result

    @pytest.mark.asyncio
    async def test_list_prs_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.pull_requests.list = AsyncMock(side_effect=Exception("API Error"))

        result = await pull_requests.list_pull_requests(
            owner="test",
            repo="test-repo",
            ctx=mock_context,
        )

        assert "Error listing pull requests" in result


class TestGetPullRequest:
    """Test get_pull_request tool."""

    @pytest.mark.asyncio
    async def test_get_pr_success(self, mock_client, mock_context):
        """Test successful PR retrieval."""
        mock_pr = MagicMock()
        mock_pr.slug = "123"
        mock_pr.title = "Test PR"
        mock_pr.status = "open"
        mock_pr.author = MagicMock(slug="authoruser")
        mock_pr.source_branch = "feature"
        mock_pr.target_branch = "main"
        mock_pr.description = "This is a test PR description"
        mock_pr.merge_info = MagicMock(
            merge_commit_hash="abc123def456",
            error=None,
        )
        mock_pr.created_at = "2024-01-01T10:00:00"
        mock_pr.updated_at = "2024-01-02T12:00:00"

        mock_client.pull_requests.get = AsyncMock(return_value=mock_pr)

        result = await pull_requests.get_pull_request(
            owner="test",
            repo="test-repo",
            pull_number=123,
            ctx=mock_context,
        )

        assert "Test PR" in result
        assert "123" in result
        assert "authoruser" in result
        assert "This is a test PR description" in result
        assert "abc123d" in result  # Shortened hash

    @pytest.mark.asyncio
    async def test_get_pr_no_description(self, mock_client, mock_context):
        """Test PR without description."""
        mock_pr = MagicMock()
        mock_pr.slug = "456"
        mock_pr.title = "Simple PR"
        mock_pr.status = "draft"
        mock_pr.author = None
        mock_pr.source_branch = "feature"
        mock_pr.target_branch = "main"
        mock_pr.description = None
        mock_pr.merge_info = None
        mock_pr.created_at = "2024-01-01"
        mock_pr.updated_at = "2024-01-01"

        mock_client.pull_requests.get = AsyncMock(return_value=mock_pr)

        result = await pull_requests.get_pull_request(
            owner="test",
            repo="test-repo",
            pull_number=456,
            ctx=mock_context,
        )

        assert "Simple PR" in result
        assert "unknown" in result
        # Description section should not appear

    @pytest.mark.asyncio
    async def test_get_pr_with_merge_error(self, mock_client, mock_context):
        """Test PR with merge error."""
        mock_pr = MagicMock()
        mock_pr.slug = "789"
        mock_pr.title = "Problematic PR"
        mock_pr.status = "merging"
        mock_pr.author = MagicMock(slug="testuser")
        mock_pr.source_branch = "feature"
        mock_pr.target_branch = "main"
        mock_pr.description = None
        mock_pr.merge_info = MagicMock(
            merge_commit_hash=None,
            error="Merge conflict detected",
        )
        mock_pr.created_at = "2024-01-01"
        mock_pr.updated_at = "2024-01-01"

        mock_client.pull_requests.get = AsyncMock(return_value=mock_pr)

        result = await pull_requests.get_pull_request(
            owner="test",
            repo="test-repo",
            pull_number=789,
            ctx=mock_context,
        )

        assert "Problematic PR" in result
        assert "Merge conflict detected" in result

    @pytest.mark.asyncio
    async def test_get_pr_all_statuses(self, mock_client, mock_context):
        """Test PR with different statuses."""
        statuses = [
            ("draft", "Draft"),
            ("open", "Open"),
            ("discarded", "Discarded"),
            ("merging", "Merging"),
            ("merged", "Merged"),
        ]

        for status, display in statuses:
            mock_pr = MagicMock()
            mock_pr.slug = "100"
            mock_pr.title = "Status Test"
            mock_pr.status = status
            mock_pr.author = MagicMock(slug="user")
            mock_pr.source_branch = "feature"
            mock_pr.target_branch = "main"
            mock_pr.description = None
            mock_pr.merge_info = None
            mock_pr.created_at = "2024-01-01"
            mock_pr.updated_at = "2024-01-01"

            mock_client.pull_requests.get = AsyncMock(return_value=mock_pr)

            result = await pull_requests.get_pull_request(
                owner="test",
                repo="test-repo",
                pull_number=100,
                ctx=mock_context,
            )

            assert display in result

    @pytest.mark.asyncio
    async def test_get_pr_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.pull_requests.get = AsyncMock(side_effect=Exception("API Error"))

        result = await pull_requests.get_pull_request(
            owner="test",
            repo="test-repo",
            pull_number=123,
            ctx=mock_context,
        )

        assert "Error getting pull request" in result


class TestCreatePullRequest:
    """Test create_pull_request tool."""

    @pytest.mark.asyncio
    async def test_create_pr_success(self, mock_client, mock_context):
        """Test successful PR creation."""
        mock_pr = MagicMock()
        mock_pr.slug = "789"
        mock_pr.title = "New Feature"
        mock_pr.source_branch = "feature-branch"
        mock_pr.target_branch = "main"
        mock_pr.author = MagicMock(slug="creator")

        mock_client.pull_requests.create = AsyncMock(return_value=mock_pr)

        result = await pull_requests.create_pull_request(
            owner="test",
            repo="test-repo",
            title="New Feature",
            source_branch="feature-branch",
            target_branch="main",
            description="Adds a new feature",
            publish=True,
            ctx=mock_context,
        )

        assert "Pull request created" in result
        assert "New Feature" in result
        assert "789" in result
        assert "published" in result
        mock_client.pull_requests.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_pr_as_draft(self, mock_client, mock_context):
        """Test creating PR as draft."""
        mock_pr = MagicMock()
        mock_pr.slug = "101"
        mock_pr.title = "Draft PR"
        mock_pr.source_branch = "wip-branch"
        mock_pr.target_branch = "main"
        mock_pr.author = MagicMock(slug="author")

        mock_client.pull_requests.create = AsyncMock(return_value=mock_pr)

        result = await pull_requests.create_pull_request(
            owner="test",
            repo="test-repo",
            title="Draft PR",
            source_branch="wip-branch",
            target_branch="main",
            description="Work in progress",
            publish=False,
            ctx=mock_context,
        )

        assert "draft" in result

    @pytest.mark.asyncio
    async def test_create_pr_with_reviewers(self, mock_client, mock_context):
        """Test creating PR with reviewers."""
        mock_pr = MagicMock()
        mock_pr.slug = "202"
        mock_pr.title = "Reviewed PR"
        mock_pr.source_branch = "feature"
        mock_pr.target_branch = "main"
        mock_pr.author = MagicMock(slug="author")

        mock_client.pull_requests.create = AsyncMock(return_value=mock_pr)

        result = await pull_requests.create_pull_request(
            owner="test",
            repo="test-repo",
            title="Reviewed PR",
            source_branch="feature",
            target_branch="main",
            reviewer_ids=["reviewer1", "reviewer2"],
            ctx=mock_context,
        )

        assert "Pull request created" in result

    @pytest.mark.asyncio
    async def test_create_pr_minimal(self, mock_client, mock_context):
        """Test creating PR with minimal fields."""
        mock_pr = MagicMock()
        mock_pr.slug = "303"
        mock_pr.title = "Minimal PR"
        mock_pr.source_branch = "patch"
        mock_pr.target_branch = "main"
        mock_pr.author = None

        mock_client.pull_requests.create = AsyncMock(return_value=mock_pr)

        result = await pull_requests.create_pull_request(
            owner="test",
            repo="test-repo",
            title="Minimal PR",
            source_branch="patch",
            target_branch="main",
            ctx=mock_context,
        )

        assert "Minimal PR" in result
        assert "unknown" in result

    @pytest.mark.asyncio
    async def test_create_pr_empty_description(self, mock_client, mock_context):
        """Test creating PR with empty description string."""
        mock_pr = MagicMock()
        mock_pr.slug = "404"
        mock_pr.title = "No Description PR"
        mock_pr.source_branch = "feature"
        mock_pr.target_branch = "main"
        mock_pr.author = MagicMock(slug="user")

        mock_client.pull_requests.create = AsyncMock(return_value=mock_pr)

        result = await pull_requests.create_pull_request(
            owner="test",
            repo="test-repo",
            title="No Description PR",
            source_branch="feature",
            target_branch="main",
            description="",  # Empty string
            ctx=mock_context,
        )

        assert "Pull request created" in result

    @pytest.mark.asyncio
    async def test_create_pr_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.pull_requests.create = AsyncMock(side_effect=Exception("API Error"))

        result = await pull_requests.create_pull_request(
            owner="test",
            repo="test-repo",
            title="Failed PR",
            source_branch="feature",
            target_branch="main",
            ctx=mock_context,
        )

        assert "Error creating pull request" in result


class TestUpdatePullRequest:
    """Test update_pull_request tool."""

    @pytest.mark.asyncio
    async def test_update_pr_both_fields(self, mock_client, mock_context):
        """Test updating both title and description."""
        mock_pr = MagicMock()
        mock_pr.slug = "123"
        mock_pr.title = "Updated Title"

        mock_client.pull_requests.update = AsyncMock(return_value=mock_pr)

        result = await pull_requests.update_pull_request(
            owner="test",
            repo="test-repo",
            pull_number=123,
            title="Updated Title",
            description="Updated description",
            ctx=mock_context,
        )

        assert "Pull request updated" in result
        assert "Updated Title" in result
        assert "123" in result

    @pytest.mark.asyncio
    async def test_update_pr_title_only(self, mock_client, mock_context):
        """Test updating only title."""
        mock_pr = MagicMock()
        mock_pr.slug = "456"
        mock_pr.title = "New Title Only"

        mock_client.pull_requests.update = AsyncMock(return_value=mock_pr)

        result = await pull_requests.update_pull_request(
            owner="test",
            repo="test-repo",
            pull_number=456,
            title="New Title Only",
            ctx=mock_context,
        )

        assert "New Title Only" in result

    @pytest.mark.asyncio
    async def test_update_pr_description_only(self, mock_client, mock_context):
        """Test updating only description."""
        mock_pr = MagicMock()
        mock_pr.slug = "789"
        mock_pr.title = "Same Title"

        mock_client.pull_requests.update = AsyncMock(return_value=mock_pr)

        result = await pull_requests.update_pull_request(
            owner="test",
            repo="test-repo",
            pull_number=789,
            description="New description only",
            ctx=mock_context,
        )

        assert "Same Title" in result

    @pytest.mark.asyncio
    async def test_update_pr_empty_description(self, mock_client, mock_context):
        """Test setting description to empty string."""
        mock_pr = MagicMock()
        mock_pr.slug = "101"
        mock_pr.title = "Clear Desc"

        mock_client.pull_requests.update = AsyncMock(return_value=mock_pr)

        result = await pull_requests.update_pull_request(
            owner="test",
            repo="test-repo",
            pull_number=101,
            description="",
            ctx=mock_context,
        )

        assert "Clear Desc" in result

    @pytest.mark.asyncio
    async def test_update_pr_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.pull_requests.update = AsyncMock(side_effect=Exception("API Error"))

        result = await pull_requests.update_pull_request(
            owner="test",
            repo="test-repo",
            pull_number=123,
            title="New Title",
            ctx=mock_context,
        )

        assert "Error updating pull request" in result


class TestMergePullRequest:
    """Test merge_pull_request tool."""

    @pytest.mark.asyncio
    async def test_merge_pr_success_with_commit(self, mock_client, mock_context):
        """Test successful merge with commit hash."""
        mock_pr = MagicMock()
        mock_pr.merge_info = MagicMock(
            merge_commit_hash="abc123def456789",
        )

        mock_client.pull_requests.merge = AsyncMock(return_value=mock_pr)

        result = await pull_requests.merge_pull_request(
            owner="test",
            repo="test-repo",
            pull_number=123,
            ctx=mock_context,
        )

        assert "merged successfully" in result
        assert "abc123d" in result

    @pytest.mark.asyncio
    async def test_merge_pr_success_no_commit(self, mock_client, mock_context):
        """Test successful merge without commit hash."""
        mock_pr = MagicMock()
        mock_pr.merge_info = None

        mock_client.pull_requests.merge = AsyncMock(return_value=mock_pr)

        result = await pull_requests.merge_pull_request(
            owner="test",
            repo="test-repo",
            pull_number=456,
            ctx=mock_context,
        )

        assert "merged successfully" in result
        assert "#456" in result

    @pytest.mark.asyncio
    async def test_merge_pr_with_all_options(self, mock_client, mock_context):
        """Test merge with all options."""
        mock_pr = MagicMock()
        mock_pr.merge_info = MagicMock(
            merge_commit_hash="xyz789abc123",
        )

        mock_client.pull_requests.merge = AsyncMock(return_value=mock_pr)

        result = await pull_requests.merge_pull_request(
            owner="test",
            repo="test-repo",
            pull_number=789,
            commit_title="Merge: Feature Branch",
            commit_message="Merging feature into main",
            squash=True,
            delete_branch=True,
            ctx=mock_context,
        )

        assert "merged successfully" in result

    @pytest.mark.asyncio
    async def test_merge_pr_squash(self, mock_client, mock_context):
        """Test squash merge."""
        mock_pr = MagicMock()
        mock_pr.merge_info = MagicMock(
            merge_commit_hash="squash123",
        )

        mock_client.pull_requests.merge = AsyncMock(return_value=mock_pr)

        result = await pull_requests.merge_pull_request(
            owner="test",
            repo="test-repo",
            pull_number=100,
            squash=True,
            ctx=mock_context,
        )

        assert "merged successfully" in result

    @pytest.mark.asyncio
    async def test_merge_pr_empty_strings(self, mock_client, mock_context):
        """Test merge with empty commit strings."""
        mock_pr = MagicMock()
        mock_pr.merge_info = MagicMock(
            merge_commit_hash="commit456",
        )

        mock_client.pull_requests.merge = AsyncMock(return_value=mock_pr)

        result = await pull_requests.merge_pull_request(
            owner="test",
            repo="test-repo",
            pull_number=200,
            commit_title="",
            commit_message="",
            ctx=mock_context,
        )

        assert "merged successfully" in result

    @pytest.mark.asyncio
    async def test_merge_pr_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.pull_requests.merge = AsyncMock(side_effect=Exception("API Error"))

        result = await pull_requests.merge_pull_request(
            owner="test",
            repo="test-repo",
            pull_number=123,
            ctx=mock_context,
        )

        assert "Error merging pull request" in result


class TestPublishPullRequest:
    """Test publish_pull_request tool."""

    @pytest.mark.asyncio
    async def test_publish_pr_success(self, mock_client, mock_context):
        """Test successful PR publish."""
        mock_pr = MagicMock()
        mock_pr.status = "open"

        mock_client.pull_requests.publish = AsyncMock(return_value=mock_pr)

        result = await pull_requests.publish_pull_request(
            owner="test",
            repo="test-repo",
            pull_number=123,
            ctx=mock_context,
        )

        assert "published" in result
        assert "123" in result
        assert "open" in result
        mock_client.pull_requests.publish.assert_called_once_with(
            owner="test",
            repo="test-repo",
            pull_number=123,
        )

    @pytest.mark.asyncio
    async def test_publish_pr_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.pull_requests.publish = AsyncMock(side_effect=Exception("API Error"))

        result = await pull_requests.publish_pull_request(
            owner="test",
            repo="test-repo",
            pull_number=123,
            ctx=mock_context,
        )

        assert "Error publishing pull request" in result


class TestDiscardPullRequest:
    """Test discard_pull_request tool."""

    @pytest.mark.asyncio
    async def test_discard_pr_success(self, mock_client, mock_context):
        """Test successful PR discard."""
        mock_pr = MagicMock()
        mock_pr.status = "discarded"

        mock_client.pull_requests.discard = AsyncMock(return_value=mock_pr)

        result = await pull_requests.discard_pull_request(
            owner="test",
            repo="test-repo",
            pull_number=123,
            ctx=mock_context,
        )

        assert "discarded" in result
        assert "123" in result
        assert "discarded" in result
        mock_client.pull_requests.discard.assert_called_once_with(
            owner="test",
            repo="test-repo",
            pull_number=123,
        )

    @pytest.mark.asyncio
    async def test_discard_pr_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.pull_requests.discard = AsyncMock(side_effect=Exception("API Error"))

        result = await pull_requests.discard_pull_request(
            owner="test",
            repo="test-repo",
            pull_number=123,
            ctx=mock_context,
        )

        assert "Error discarding pull request" in result


class TestListPRReviewers:
    """Test list_pr_reviewers tool."""

    @pytest.mark.asyncio
    async def test_list_reviewers_success(self, mock_client, mock_context):
        """Test successful reviewer listing."""
        mock_reviewer = MagicMock()
        mock_reviewer.user = MagicMock(slug="reviewer1")
        mock_reviewer.review_decision = "approve"

        mock_result = MagicMock()
        mock_result.reviewers = [mock_reviewer]

        mock_client.pull_requests.list_reviewers = AsyncMock(return_value=mock_result)

        result = await pull_requests.list_pr_reviewers(
            owner="test",
            repo="test-repo",
            pull_number=123,
            ctx=mock_context,
        )

        assert "Reviewers for PR #123" in result
        assert "reviewer1" in result
        assert "approve" in result

    @pytest.mark.asyncio
    async def test_list_reviewers_empty(self, mock_client, mock_context):
        """Test listing with no reviewers."""
        mock_result = MagicMock()
        mock_result.reviewers = []

        mock_client.pull_requests.list_reviewers = AsyncMock(return_value=mock_result)

        result = await pull_requests.list_pr_reviewers(
            owner="test",
            repo="test-repo",
            pull_number=456,
            ctx=mock_context,
        )

        assert "No reviewers assigned" in result

    @pytest.mark.asyncio
    async def test_list_reviewers_all_decisions(self, mock_client, mock_context):
        """Test all review decision types."""
        decisions = [
            ("approve", "✅"),
            ("trust", "🤝"),
            ("block", "🚫"),
            ("abstain", "➖"),
        ]

        for decision, icon in decisions:
            mock_reviewer = MagicMock()
            mock_reviewer.user = MagicMock(slug=f"user-{decision}")
            mock_reviewer.review_decision = decision

            mock_result = MagicMock()
            mock_result.reviewers = [mock_reviewer]

            mock_client.pull_requests.list_reviewers = AsyncMock(return_value=mock_result)

            result = await pull_requests.list_pr_reviewers(
                owner="test",
                repo="test-repo",
                pull_number=100,
                ctx=mock_context,
            )

            assert f"user-{decision}" in result
            assert decision in result

    @pytest.mark.asyncio
    async def test_list_reviewers_no_decision(self, mock_client, mock_context):
        """Test reviewer with no decision."""
        mock_reviewer = MagicMock()
        mock_reviewer.user = MagicMock(slug="pending-reviewer")
        mock_reviewer.review_decision = None

        mock_result = MagicMock()
        mock_result.reviewers = [mock_reviewer]

        mock_client.pull_requests.list_reviewers = AsyncMock(return_value=mock_result)

        result = await pull_requests.list_pr_reviewers(
            owner="test",
            repo="test-repo",
            pull_number=789,
            ctx=mock_context,
        )

        assert "pending-reviewer" in result
        assert "no decision" in result
        assert "⏳" in result

    @pytest.mark.asyncio
    async def test_list_reviewers_result_without_reviewers_attr(self, mock_client, mock_context):
        """Test when result doesn't have reviewers attribute."""
        mock_result = []  # Not a MagicMock with reviewers attribute

        mock_client.pull_requests.list_reviewers = AsyncMock(return_value=mock_result)

        result = await pull_requests.list_pr_reviewers(
            owner="test",
            repo="test-repo",
            pull_number=999,
            ctx=mock_context,
        )

        assert "No reviewers assigned" in result

    @pytest.mark.asyncio
    async def test_list_reviewers_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.pull_requests.list_reviewers = AsyncMock(side_effect=Exception("API Error"))

        result = await pull_requests.list_pr_reviewers(
            owner="test",
            repo="test-repo",
            pull_number=123,
            ctx=mock_context,
        )

        assert "Error listing reviewers" in result


class TestAddPRReviewer:
    """Test add_pr_reviewer tool."""

    @pytest.mark.asyncio
    async def test_add_reviewer_success(self, mock_client, mock_context):
        """Test successful reviewer addition."""
        mock_client.pull_requests.add_reviewer = AsyncMock(return_value=None)

        result = await pull_requests.add_pr_reviewer(
            owner="test",
            repo="test-repo",
            pull_number=123,
            user_id="revieweruser",
            ctx=mock_context,
        )

        assert "Reviewer added" in result
        assert "123" in result
        mock_client.pull_requests.add_reviewer.assert_called_once_with(
            owner="test",
            repo="test-repo",
            pull_number=123,
            user_id="revieweruser",
        )

    @pytest.mark.asyncio
    async def test_add_reviewer_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.pull_requests.add_reviewer = AsyncMock(side_effect=Exception("API Error"))

        result = await pull_requests.add_pr_reviewer(
            owner="test",
            repo="test-repo",
            pull_number=123,
            user_id="revieweruser",
            ctx=mock_context,
        )

        assert "Error adding reviewer" in result


class TestSetReviewDecision:
    """Test set_review_decision tool."""

    @pytest.mark.asyncio
    async def test_set_decision_approve(self, mock_client, mock_context):
        """Test setting approve decision."""
        mock_client.pull_requests.set_review_decision = AsyncMock(return_value=None)

        result = await pull_requests.set_review_decision(
            owner="test",
            repo="test-repo",
            pull_number=123,
            decision="approve",
            ctx=mock_context,
        )

        assert "approve" in result
        assert "123" in result
        mock_client.pull_requests.set_review_decision.assert_called_once_with(
            owner="test",
            repo="test-repo",
            pull_number=123,
            decision="approve",
        )

    @pytest.mark.asyncio
    async def test_set_decision_block(self, mock_client, mock_context):
        """Test setting block decision."""
        mock_client.pull_requests.set_review_decision = AsyncMock(return_value=None)

        result = await pull_requests.set_review_decision(
            owner="test",
            repo="test-repo",
            pull_number=456,
            decision="block",
            ctx=mock_context,
        )

        assert "block" in result
        assert "456" in result

    @pytest.mark.asyncio
    async def test_set_decision_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.pull_requests.set_review_decision = AsyncMock(
            side_effect=Exception("API Error")
        )

        result = await pull_requests.set_review_decision(
            owner="test",
            repo="test-repo",
            pull_number=123,
            decision="approve",
            ctx=mock_context,
        )

        assert "Error setting review decision" in result
