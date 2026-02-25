"""Tests for repository tools."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from sourcecraft_mcp.tools import repositories


class TestListRepositories:
    """Test list_repositories tool."""

    @pytest.mark.asyncio
    async def test_list_repositories_success(self, mock_client, mock_context):
        """Test successful repository listing."""
        # Setup mock
        mock_repo = MagicMock()
        mock_repo.slug = "test-repo"
        mock_repo.name = "Test Repo"
        mock_repo.description = "Test description"
        mock_repo.visibility = "public"
        mock_repo.language = MagicMock(name="Python")
        mock_repo.last_updated = "2024-01-15"

        mock_result = MagicMock()
        mock_result.repositories = [mock_repo]
        mock_result.next_page_token = None

        mock_client.repositories.list = AsyncMock(return_value=mock_result)

        # Call the tool
        result = await repositories.list_repositories(
            username="testuser",
            ctx=mock_context,
        )

        # Verify
        assert "Test Repo" in result
        assert "test-repo" in result
        assert "Test description" in result
        mock_client.repositories.list.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_repositories_empty(self, mock_client, mock_context):
        """Test listing with no repositories."""
        mock_result = MagicMock()
        mock_result.repositories = []

        mock_client.repositories.list = AsyncMock(return_value=mock_result)

        result = await repositories.list_repositories(ctx=mock_context)

        assert "No repositories found" in result

    @pytest.mark.asyncio
    async def test_list_repositories_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.repositories.list = AsyncMock(side_effect=Exception("API Error"))

        result = await repositories.list_repositories(ctx=mock_context)

        assert "Error listing repositories" in result

    @pytest.mark.asyncio
    async def test_list_repositories_private(self, mock_client, mock_context):
        """Test listing with private repository."""
        mock_repo = MagicMock()
        mock_repo.slug = "private-repo"
        mock_repo.name = "Private Repo"
        mock_repo.description = "Private description"
        mock_repo.visibility = "private"
        mock_repo.language = MagicMock(name="Python")
        mock_repo.last_updated = "2024-01-15"

        mock_result = MagicMock()
        mock_result.repositories = [mock_repo]
        mock_result.next_page_token = None

        mock_client.repositories.list = AsyncMock(return_value=mock_result)

        result = await repositories.list_repositories(ctx=mock_context)

        assert "Private Repo" in result
        assert "private-repo" in result

    @pytest.mark.asyncio
    async def test_list_repositories_pagination(self, mock_client, mock_context):
        """Test listing with pagination."""
        mock_repo = MagicMock()
        mock_repo.slug = "test-repo"
        mock_repo.name = "Test Repo"
        mock_repo.description = "Test description"
        mock_repo.visibility = "public"
        mock_repo.language = MagicMock(name="Python")
        mock_repo.last_updated = "2024-01-15"

        mock_result = MagicMock()
        mock_result.repositories = [mock_repo]
        mock_result.next_page_token = "next_token"

        mock_client.repositories.list = AsyncMock(return_value=mock_result)

        result = await repositories.list_repositories(
            username="testuser",
            page=1,
            per_page=10,
            ctx=mock_context,
        )

        assert "Test Repo" in result
        assert "More results available" in result
        assert "page=2" in result
        mock_client.repositories.list.assert_called_once_with(
            username="testuser",
            page=1,
            per_page=10,
        )

    @pytest.mark.asyncio
    async def test_list_repositories_no_language(self, mock_client, mock_context):
        """Test listing repository with no language."""
        mock_repo = MagicMock()
        mock_repo.slug = "test-repo"
        mock_repo.name = "Test Repo"
        mock_repo.description = "Test description"
        mock_repo.visibility = "public"
        mock_repo.language = None
        mock_repo.last_updated = "2024-01-15"

        mock_result = MagicMock()
        mock_result.repositories = [mock_repo]
        mock_result.next_page_token = None

        mock_client.repositories.list = AsyncMock(return_value=mock_result)

        result = await repositories.list_repositories(ctx=mock_context)

        assert "Unknown" in result


class TestGetRepository:
    """Test get_repository tool."""

    @pytest.mark.asyncio
    async def test_get_repository_success(self, mock_client, mock_context):
        """Test successful repository retrieval."""
        mock_repo = MagicMock()
        mock_repo.slug = "test-repo"
        mock_repo.name = "Test Repo"
        mock_repo.description = "A test repository"
        mock_repo.visibility = "public"
        mock_repo.default_branch = "main"
        mock_repo.is_empty = False
        mock_repo.web_url = "https://sourcecraft.dev/test/test-repo"
        mock_repo.language = MagicMock(name="Python")
        mock_repo.counters = MagicMock(forks="10", pull_requests="5", issues="3")
        mock_repo.clone_url = MagicMock(
            ssh="git@sourcecraft.dev:test/test-repo.git",
            https="https://sourcecraft.dev/test/test-repo.git",
        )
        mock_repo.last_updated = "2024-01-15"

        mock_client.repositories.get = AsyncMock(return_value=mock_repo)

        result = await repositories.get_repository(
            owner="test",
            repo="test-repo",
            ctx=mock_context,
        )

        assert "test-repo" in result
        assert "Test Repo" in result
        assert "A test repository" in result
        assert "main" in result
        assert "10 forks" in result

    @pytest.mark.asyncio
    async def test_get_repository_private(self, mock_client, mock_context):
        """Test getting private repository."""
        mock_repo = MagicMock()
        mock_repo.slug = "private-repo"
        mock_repo.name = "Private Repo"
        mock_repo.description = "A private repository"
        mock_repo.visibility = "private"
        mock_repo.default_branch = "main"
        mock_repo.is_empty = False
        mock_repo.web_url = "https://sourcecraft.dev/test/private-repo"
        mock_repo.language = None
        mock_repo.counters = None
        mock_repo.clone_url = MagicMock(
            ssh="git@sourcecraft.dev:test/private-repo.git",
            https="https://sourcecraft.dev/test/private-repo.git",
        )
        mock_repo.last_updated = "2024-01-15"

        mock_client.repositories.get = AsyncMock(return_value=mock_repo)

        result = await repositories.get_repository(
            owner="test",
            repo="private-repo",
            ctx=mock_context,
        )

        assert "Private" in result
        assert "private-repo" in result

    @pytest.mark.asyncio
    async def test_get_repository_empty(self, mock_client, mock_context):
        """Test getting empty repository."""
        mock_repo = MagicMock()
        mock_repo.slug = "empty-repo"
        mock_repo.name = "Empty Repo"
        mock_repo.description = None
        mock_repo.visibility = "public"
        mock_repo.default_branch = "main"
        mock_repo.is_empty = True
        mock_repo.web_url = "https://sourcecraft.dev/test/empty-repo"
        mock_repo.language = None
        mock_repo.counters = None
        mock_repo.clone_url = None
        mock_repo.last_updated = "2024-01-15"

        mock_client.repositories.get = AsyncMock(return_value=mock_repo)

        result = await repositories.get_repository(
            owner="test",
            repo="empty-repo",
            ctx=mock_context,
        )

        assert "Empty: Yes" in result
        assert "No description" in result
        assert "N/A" in result

    @pytest.mark.asyncio
    async def test_get_repository_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.repositories.get = AsyncMock(side_effect=Exception("API Error"))

        result = await repositories.get_repository(
            owner="test",
            repo="test-repo",
            ctx=mock_context,
        )

        assert "Error getting repository" in result


def capture_tool(captured_tools):
    """Create a decorator that captures the decorated function."""

    def decorator(f):
        captured_tools[f.__name__] = f
        return f

    return decorator


class TestRegisterTools:
    """Test register_tools function."""

    def test_register_tools_registers_all_tools(self):
        """Test that all tools are registered."""
        mcp = MagicMock()
        captured_tools = {}
        mcp.tool = MagicMock(return_value=capture_tool(captured_tools))

        repositories.register_tools(mcp)

        assert mcp.tool.call_count == 9
        assert "_list_repositories" in captured_tools
        assert "list_organization_repositories" in captured_tools
        assert "_get_repository" in captured_tools
        assert "create_repository" in captured_tools
        assert "update_repository" in captured_tools
        assert "delete_repository" in captured_tools
        assert "list_branches" in captured_tools
        assert "list_tags" in captured_tools
        assert "get_file_tree" in captured_tools


class TestListOrganizationRepositories:
    """Test list_organization_repositories tool."""

    @pytest.fixture
    def tool_func(self):
        """Get the tool function."""
        mcp = MagicMock()
        captured_tools = {}
        mcp.tool = MagicMock(return_value=capture_tool(captured_tools))
        repositories.register_tools(mcp)
        return captured_tools["list_organization_repositories"]

    @pytest.mark.asyncio
    async def test_list_organization_repositories_success(
        self, mock_client, mock_context, tool_func
    ):
        """Test successful organization repository listing."""
        mock_repo = MagicMock()
        mock_repo.slug = "org-repo"
        mock_repo.name = "Org Repo"
        mock_repo.description = "Organization repository"
        mock_repo.visibility = "public"

        mock_result = MagicMock()
        mock_result.repositories = [mock_repo]

        mock_client.repositories.list_org_repos = AsyncMock(return_value=mock_result)

        result = await tool_func(org="test-org", page=1, per_page=30, ctx=mock_context)

        assert "Org Repo" in result
        assert "org-repo" in result
        assert "test-org" in result

    @pytest.mark.asyncio
    async def test_list_organization_repositories_empty(self, mock_client, mock_context, tool_func):
        """Test listing with no organization repositories."""
        mock_result = MagicMock()
        mock_result.repositories = []

        mock_client.repositories.list_org_repos = AsyncMock(return_value=mock_result)

        result = await tool_func(org="test-org", ctx=mock_context)

        assert "No repositories found" in result
        assert "test-org" in result

    @pytest.mark.asyncio
    async def test_list_organization_repositories_error(self, mock_client, mock_context, tool_func):
        """Test error handling."""
        mock_client.repositories.list_org_repos = AsyncMock(side_effect=Exception("API Error"))

        result = await tool_func(org="test-org", ctx=mock_context)

        assert "Error listing organization repositories" in result


class TestCreateRepository:
    """Test create_repository tool."""

    @pytest.fixture
    def tool_func(self):
        """Get the tool function."""
        mcp = MagicMock()
        captured_tools = {}
        mcp.tool = MagicMock(return_value=capture_tool(captured_tools))
        repositories.register_tools(mcp)
        return captured_tools["create_repository"]

    @pytest.mark.asyncio
    async def test_create_repository_success(self, mock_client, mock_context, tool_func):
        """Test successful repository creation."""
        mock_repo = MagicMock()
        mock_repo.name = "New Repo"
        mock_repo.slug = "new-repo"
        mock_repo.visibility = "private"
        mock_repo.default_branch = "main"
        mock_repo.web_url = "https://sourcecraft.dev/user/new-repo"
        mock_repo.clone_url = MagicMock(ssh="git@sourcecraft.dev:user/new-repo.git")

        mock_client.repositories.create = AsyncMock(return_value=mock_repo)

        result = await tool_func(
            name="new-repo",
            description="A new repository",
            visibility="private",
            ctx=mock_context,
        )

        assert "Repository created successfully" in result
        assert "new-repo" in result
        assert "main" in result

    @pytest.mark.asyncio
    async def test_create_repository_public(self, mock_client, mock_context, tool_func):
        """Test creating public repository."""
        mock_repo = MagicMock()
        mock_repo.name = "Public Repo"
        mock_repo.slug = "public-repo"
        mock_repo.visibility = "public"
        mock_repo.default_branch = "main"
        mock_repo.web_url = "https://sourcecraft.dev/user/public-repo"
        mock_repo.clone_url = MagicMock(ssh="git@sourcecraft.dev:user/public-repo.git")

        mock_client.repositories.create = AsyncMock(return_value=mock_repo)

        result = await tool_func(
            name="public-repo",
            description="",
            visibility="public",
            ctx=mock_context,
        )

        assert "Repository created successfully" in result
        assert "public" in result

    @pytest.mark.asyncio
    async def test_create_repository_error(self, mock_client, mock_context, tool_func):
        """Test error handling."""
        mock_client.repositories.create = AsyncMock(side_effect=Exception("API Error"))

        result = await tool_func(
            name="new-repo",
            description="A new repository",
            ctx=mock_context,
        )

        assert "Error creating repository" in result


class TestUpdateRepository:
    """Test update_repository tool."""

    @pytest.fixture
    def tool_func(self):
        """Get the tool function."""
        mcp = MagicMock()
        captured_tools = {}
        mcp.tool = MagicMock(return_value=capture_tool(captured_tools))
        repositories.register_tools(mcp)
        return captured_tools["update_repository"]

    @pytest.mark.asyncio
    async def test_update_repository_success(self, mock_client, mock_context, tool_func):
        """Test successful repository update."""
        mock_repo = MagicMock()
        mock_repo.name = "Updated Repo"
        mock_repo.description = "Updated description"
        mock_repo.default_branch = "develop"
        mock_repo.visibility = "public"

        mock_client.repositories.update = AsyncMock(return_value=mock_repo)

        result = await tool_func(
            owner="test",
            repo="test-repo",
            description="Updated description",
            default_branch="develop",
            visibility="public",
            ctx=mock_context,
        )

        assert "Repository updated successfully" in result
        assert "Updated description" in result
        assert "develop" in result

    @pytest.mark.asyncio
    async def test_update_repository_partial(self, mock_client, mock_context, tool_func):
        """Test partial repository update."""
        mock_repo = MagicMock()
        mock_repo.name = "Updated Repo"
        mock_repo.description = "Only description"
        mock_repo.default_branch = "main"
        mock_repo.visibility = "private"

        mock_client.repositories.update = AsyncMock(return_value=mock_repo)

        result = await tool_func(
            owner="test",
            repo="test-repo",
            description="Only description",
            ctx=mock_context,
        )

        assert "Repository updated successfully" in result

    @pytest.mark.asyncio
    async def test_update_repository_error(self, mock_client, mock_context, tool_func):
        """Test error handling."""
        mock_client.repositories.update = AsyncMock(side_effect=Exception("API Error"))

        result = await tool_func(
            owner="test",
            repo="test-repo",
            description="Updated",
            ctx=mock_context,
        )

        assert "Error updating repository" in result


class TestDeleteRepository:
    """Test delete_repository tool."""

    @pytest.fixture
    def tool_func(self):
        """Get the tool function."""
        mcp = MagicMock()
        captured_tools = {}
        mcp.tool = MagicMock(return_value=capture_tool(captured_tools))
        repositories.register_tools(mcp)
        return captured_tools["delete_repository"]

    @pytest.mark.asyncio
    async def test_delete_repository_success(self, mock_client, mock_context, tool_func):
        """Test successful repository deletion."""
        mock_client.repositories.delete = AsyncMock(return_value=None)

        result = await tool_func(
            owner="test",
            repo="test-repo",
            ctx=mock_context,
        )

        assert "deleted successfully" in result
        assert "test/test-repo" in result
        mock_client.repositories.delete.assert_called_once_with(
            owner="test",
            repo="test-repo",
        )

    @pytest.mark.asyncio
    async def test_delete_repository_error(self, mock_client, mock_context, tool_func):
        """Test error handling."""
        mock_client.repositories.delete = AsyncMock(side_effect=Exception("API Error"))

        result = await tool_func(
            owner="test",
            repo="test-repo",
            ctx=mock_context,
        )

        assert "Error deleting repository" in result


class TestListBranches:
    """Test list_branches tool."""

    @pytest.fixture
    def tool_func(self):
        """Get the tool function."""
        mcp = MagicMock()
        captured_tools = {}
        mcp.tool = MagicMock(return_value=capture_tool(captured_tools))
        repositories.register_tools(mcp)
        return captured_tools["list_branches"]

    @pytest.mark.asyncio
    async def test_list_branches_success(self, mock_client, mock_context, tool_func):
        """Test successful branch listing."""
        mock_branch = MagicMock()
        mock_branch.name = "main"
        mock_branch.commit = MagicMock(hash="abc1234567890")

        mock_result = MagicMock()
        mock_result.branches = [mock_branch]

        mock_client.repositories.list_branches = AsyncMock(return_value=mock_result)

        result = await tool_func(
            owner="test",
            repo="test-repo",
            ctx=mock_context,
        )

        assert "Branches in" in result
        assert "main" in result
        assert "abc1234" in result

    @pytest.mark.asyncio
    async def test_list_branches_no_commit(self, mock_client, mock_context, tool_func):
        """Test listing branches without commit info."""
        mock_branch = MagicMock()
        mock_branch.name = "feature"
        mock_branch.commit = None

        mock_result = MagicMock()
        mock_result.branches = [mock_branch]

        mock_client.repositories.list_branches = AsyncMock(return_value=mock_result)

        result = await tool_func(
            owner="test",
            repo="test-repo",
            ctx=mock_context,
        )

        assert "feature" in result

    @pytest.mark.asyncio
    async def test_list_branches_empty(self, mock_client, mock_context, tool_func):
        """Test listing with no branches."""
        mock_result = MagicMock()
        mock_result.branches = []

        mock_client.repositories.list_branches = AsyncMock(return_value=mock_result)

        result = await tool_func(
            owner="test",
            repo="test-repo",
            ctx=mock_context,
        )

        assert "No branches found" in result

    @pytest.mark.asyncio
    async def test_list_branches_error(self, mock_client, mock_context, tool_func):
        """Test error handling."""
        mock_client.repositories.list_branches = AsyncMock(side_effect=Exception("API Error"))

        result = await tool_func(
            owner="test",
            repo="test-repo",
            ctx=mock_context,
        )

        assert "Error listing branches" in result


class TestListTags:
    """Test list_tags tool."""

    @pytest.fixture
    def tool_func(self):
        """Get the tool function."""
        mcp = MagicMock()
        captured_tools = {}
        mcp.tool = MagicMock(return_value=capture_tool(captured_tools))
        repositories.register_tools(mcp)
        return captured_tools["list_tags"]

    @pytest.mark.asyncio
    async def test_list_tags_success(self, mock_client, mock_context, tool_func):
        """Test successful tag listing."""
        mock_tag = MagicMock()
        mock_tag.name = "v1.0.0"
        mock_tag.commit = MagicMock(hash="abc1234567890")
        mock_tag.target = "main"

        mock_result = MagicMock()
        mock_result.tags = [mock_tag]

        mock_client.repositories.list_tags = AsyncMock(return_value=mock_result)

        result = await tool_func(
            owner="test",
            repo="test-repo",
            ctx=mock_context,
        )

        assert "Tags in" in result
        assert "v1.0.0" in result
        assert "abc1234" in result
        assert "main" in result

    @pytest.mark.asyncio
    async def test_list_tags_no_commit(self, mock_client, mock_context, tool_func):
        """Test listing tags without commit info."""
        mock_tag = MagicMock()
        mock_tag.name = "v0.1.0"
        mock_tag.commit = None
        mock_tag.target = None

        mock_result = MagicMock()
        mock_result.tags = [mock_tag]

        mock_client.repositories.list_tags = AsyncMock(return_value=mock_result)

        result = await tool_func(
            owner="test",
            repo="test-repo",
            ctx=mock_context,
        )

        assert "v0.1.0" in result

    @pytest.mark.asyncio
    async def test_list_tags_empty(self, mock_client, mock_context, tool_func):
        """Test listing with no tags."""
        mock_result = MagicMock()
        mock_result.tags = []

        mock_client.repositories.list_tags = AsyncMock(return_value=mock_result)

        result = await tool_func(
            owner="test",
            repo="test-repo",
            ctx=mock_context,
        )

        assert "No tags found" in result

    @pytest.mark.asyncio
    async def test_list_tags_error(self, mock_client, mock_context, tool_func):
        """Test error handling."""
        mock_client.repositories.list_tags = AsyncMock(side_effect=Exception("API Error"))

        result = await tool_func(
            owner="test",
            repo="test-repo",
            ctx=mock_context,
        )

        assert "Error listing tags" in result


class TestGetFileTree:
    """Test get_file_tree tool."""

    @pytest.fixture
    def tool_func(self):
        """Get the tool function."""
        mcp = MagicMock()
        captured_tools = {}
        mcp.tool = MagicMock(return_value=capture_tool(captured_tools))
        repositories.register_tools(mcp)
        return captured_tools["get_file_tree"]

    @pytest.mark.asyncio
    async def test_get_file_tree_success(self, mock_client, mock_context, tool_func):
        """Test successful file tree retrieval."""
        mock_file = MagicMock()
        mock_file.path = "README.md"
        mock_file.type = "file"

        mock_dir = MagicMock()
        mock_dir.path = "src"
        mock_dir.type = "directory"

        mock_result = MagicMock()
        mock_result.trees = [mock_file, mock_dir]

        mock_client.repositories.get_file_tree = AsyncMock(return_value=mock_result)

        result = await tool_func(
            owner="test",
            repo="test-repo",
            ctx=mock_context,
        )

        assert "Files in" in result
        assert "README.md" in result
        assert "src" in result

    @pytest.mark.asyncio
    async def test_get_file_tree_with_path(self, mock_client, mock_context, tool_func):
        """Test file tree with specific path."""
        mock_file = MagicMock()
        mock_file.path = "main.py"
        mock_file.type = "file"

        mock_result = MagicMock()
        mock_result.trees = [mock_file]

        mock_client.repositories.get_file_tree = AsyncMock(return_value=mock_result)

        result = await tool_func(
            owner="test",
            repo="test-repo",
            path="src",
            revision="main",
            recursive=True,
            ctx=mock_context,
        )

        assert "src" in result
        assert "main.py" in result

    @pytest.mark.asyncio
    async def test_get_file_tree_empty(self, mock_client, mock_context, tool_func):
        """Test empty file tree."""
        mock_result = MagicMock()
        mock_result.trees = []

        mock_client.repositories.get_file_tree = AsyncMock(return_value=mock_result)

        result = await tool_func(
            owner="test",
            repo="test-repo",
            path="empty",
            ctx=mock_context,
        )

        assert "No files found" in result
        assert "empty" in result

    @pytest.mark.asyncio
    async def test_get_file_tree_error(self, mock_client, mock_context, tool_func):
        """Test error handling."""
        mock_client.repositories.get_file_tree = AsyncMock(side_effect=Exception("API Error"))

        result = await tool_func(
            owner="test",
            repo="test-repo",
            ctx=mock_context,
        )

        assert "Error getting file tree" in result


class TestWrapperTools:
    """Test wrapper tool functions."""

    @pytest.fixture
    def captured_tools(self):
        """Get all captured tool functions."""
        mcp = MagicMock()
        captured = {}
        mcp.tool = MagicMock(return_value=capture_tool(captured))
        repositories.register_tools(mcp)
        return captured

    @pytest.mark.asyncio
    async def test_list_repositories_wrapper(self, mock_client, mock_context, captured_tools):
        """Test _list_repositories wrapper."""
        mock_repo = MagicMock()
        mock_repo.slug = "test-repo"
        mock_repo.name = "Test Repo"
        mock_repo.description = "Test"
        mock_repo.visibility = "public"
        mock_repo.language = MagicMock(name="Python")
        mock_repo.last_updated = "2024-01-15"

        mock_result = MagicMock()
        mock_result.repositories = [mock_repo]
        mock_result.next_page_token = None

        mock_client.repositories.list = AsyncMock(return_value=mock_result)

        tool_func = captured_tools["_list_repositories"]
        result = await tool_func(
            username="testuser",
            page=1,
            per_page=30,
            ctx=mock_context,
        )

        assert "Test Repo" in result

    @pytest.mark.asyncio
    async def test_get_repository_wrapper(self, mock_client, mock_context, captured_tools):
        """Test _get_repository wrapper."""
        mock_repo = MagicMock()
        mock_repo.slug = "test-repo"
        mock_repo.name = "Test Repo"
        mock_repo.description = "Test"
        mock_repo.visibility = "public"
        mock_repo.default_branch = "main"
        mock_repo.is_empty = False
        mock_repo.web_url = "https://sourcecraft.dev/test/test-repo"
        mock_repo.language = None
        mock_repo.counters = None
        mock_repo.clone_url = None
        mock_repo.last_updated = "2024-01-15"

        mock_client.repositories.get = AsyncMock(return_value=mock_repo)

        tool_func = captured_tools["_get_repository"]
        result = await tool_func(
            owner="test",
            repo="test-repo",
            ctx=mock_context,
        )

        assert "test-repo" in result
