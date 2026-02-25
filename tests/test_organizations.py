"""Tests for organization tools."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from sourcecraft_mcp.tools import organizations


class TestListOrganizations:
    """Test list_organizations tool."""

    @pytest.mark.asyncio
    async def test_list_organizations_success(self, mock_client, mock_context):
        """Test successful organization listing."""
        mock_org1 = MagicMock()
        mock_org1.slug = "org1"
        mock_org1.name = "Organization One"

        mock_org2 = MagicMock()
        mock_org2.slug = "org2"
        mock_org2.name = None

        mock_result = MagicMock()
        mock_result.organizations = [mock_org1, mock_org2]

        mock_client.organizations.list = AsyncMock(return_value=mock_result)

        result = await organizations.list_organizations(ctx=mock_context)

        assert "Organizations (2)" in result
        assert "org1" in result
        assert "Organization One" in result
        assert "org2" in result
        assert "N/A" in result

    @pytest.mark.asyncio
    async def test_list_organizations_empty(self, mock_client, mock_context):
        """Test listing with no organizations."""
        mock_result = MagicMock()
        mock_result.organizations = []

        mock_client.organizations.list = AsyncMock(return_value=mock_result)

        result = await organizations.list_organizations(ctx=mock_context)

        assert "No organizations found" == result

    @pytest.mark.asyncio
    async def test_list_organizations_no_organizations_attr(self, mock_client, mock_context):
        """Test listing when result has no organizations attribute."""
        mock_result = MagicMock()
        del mock_result.organizations

        mock_client.organizations.list = AsyncMock(return_value=mock_result)

        result = await organizations.list_organizations(ctx=mock_context)

        assert "No organizations found" == result

    @pytest.mark.asyncio
    async def test_list_organizations_with_pagination(self, mock_client, mock_context):
        """Test listing with pagination parameters."""
        mock_result = MagicMock()
        mock_result.organizations = []

        mock_client.organizations.list = AsyncMock(return_value=mock_result)

        result = await organizations.list_organizations(page=2, per_page=50, ctx=mock_context)

        mock_client.organizations.list.assert_called_once_with(page=2, per_page=50)
        assert "No organizations found" == result

    @pytest.mark.asyncio
    async def test_list_organizations_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.organizations.list = AsyncMock(side_effect=Exception("API Error"))

        result = await organizations.list_organizations(ctx=mock_context)

        assert "Error listing organizations" in result
        assert "API Error" in result


class TestGetOrganization:
    """Test get_organization tool."""

    @pytest.mark.asyncio
    async def test_get_organization_success_full(self, mock_client, mock_context):
        """Test successful organization retrieval with all fields."""
        mock_org = MagicMock()
        mock_org.slug = "myorg"
        mock_org.name = "My Organization"
        mock_org.description = "A test organization"
        mock_org.website = "https://example.com"
        mock_org.created_at = "2024-01-15T10:30:00Z"

        mock_client.organizations.get = AsyncMock(return_value=mock_org)

        result = await organizations.get_organization(org="myorg", ctx=mock_context)

        assert "myorg" in result
        assert "My Organization" in result
        assert "A test organization" in result
        assert "https://example.com" in result
        assert "2024-01-15" in result

    @pytest.mark.asyncio
    async def test_get_organization_minimal(self, mock_client, mock_context):
        """Test organization with minimal fields."""
        mock_org = MagicMock()
        mock_org.slug = "minimal"
        mock_org.name = None
        mock_org.description = None
        mock_org.website = None
        mock_org.created_at = None

        # Delete attributes that are checked with hasattr
        del mock_org.description
        del mock_org.website
        del mock_org.created_at

        mock_client.organizations.get = AsyncMock(return_value=mock_org)

        result = await organizations.get_organization(org="minimal", ctx=mock_context)

        assert "minimal" in result
        assert "N/A" in result
        assert "Description" not in result
        assert "Website" not in result
        assert "Created" not in result

    @pytest.mark.asyncio
    async def test_get_organization_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.organizations.get = AsyncMock(side_effect=Exception("API Error"))

        result = await organizations.get_organization(org="unknown", ctx=mock_context)

        assert "Error getting organization" in result


class TestListOrganizationRepositories:
    """Test list_organization_repositories tool."""

    @pytest.mark.asyncio
    async def test_list_repositories_success(self, mock_client, mock_context):
        """Test successful repository listing."""
        mock_repo1 = MagicMock()
        mock_repo1.slug = "repo1"
        mock_repo1.visibility = "public"
        mock_repo1.description = "First repo"

        mock_repo2 = MagicMock()
        mock_repo2.slug = "repo2"
        mock_repo2.visibility = "private"
        mock_repo2.description = None

        mock_result = MagicMock()
        mock_result.repositories = [mock_repo1, mock_repo2]

        mock_client.organizations.list_repos = AsyncMock(return_value=mock_result)

        result = await organizations.list_organization_repositories(org="myorg", ctx=mock_context)

        assert "Repositories in 'myorg' (2)" in result
        assert "repo1" in result
        assert "repo2" in result
        assert "First repo" in result
        assert "No description" in result

    @pytest.mark.asyncio
    async def test_list_repositories_empty(self, mock_client, mock_context):
        """Test listing with no repositories."""
        mock_result = MagicMock()
        mock_result.repositories = []

        mock_client.organizations.list_repos = AsyncMock(return_value=mock_result)

        result = await organizations.list_organization_repositories(org="myorg", ctx=mock_context)

        assert "No repositories found in organization 'myorg'" == result

    @pytest.mark.asyncio
    async def test_list_repositories_no_attr(self, mock_client, mock_context):
        """Test listing when result has no repositories attribute."""
        mock_result = MagicMock()
        del mock_result.repositories

        mock_client.organizations.list_repos = AsyncMock(return_value=mock_result)

        result = await organizations.list_organization_repositories(org="myorg", ctx=mock_context)

        assert "No repositories found in organization 'myorg'" == result

    @pytest.mark.asyncio
    async def test_list_repositories_with_pagination(self, mock_client, mock_context):
        """Test listing with pagination."""
        mock_result = MagicMock()
        mock_result.repositories = []

        mock_client.organizations.list_repos = AsyncMock(return_value=mock_result)

        await organizations.list_organization_repositories(
            org="myorg", page=3, per_page=25, ctx=mock_context
        )

        mock_client.organizations.list_repos.assert_called_once_with(
            org="myorg", page=3, per_page=25
        )

    @pytest.mark.asyncio
    async def test_list_repositories_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.organizations.list_repos = AsyncMock(side_effect=Exception("API Error"))

        result = await organizations.list_organization_repositories(org="myorg", ctx=mock_context)

        assert "Error listing organization repositories" in result


class TestListOrganizationMembers:
    """Test list_organization_members tool."""

    @pytest.mark.asyncio
    async def test_list_members_success_with_user(self, mock_client, mock_context):
        """Test successful member listing with user attribute."""
        mock_member1 = MagicMock()
        mock_member1.user = MagicMock()
        mock_member1.user.slug = "user1"
        mock_member1.role = "owner"

        mock_member2 = MagicMock()
        mock_member2.user = MagicMock()
        mock_member2.user.slug = "user2"
        mock_member2.role = "member"

        mock_result = MagicMock()
        mock_result.members = [mock_member1, mock_member2]

        mock_client.organizations.list_members = AsyncMock(return_value=mock_result)

        result = await organizations.list_organization_members(org="myorg", ctx=mock_context)

        assert "Members of 'myorg' (2)" in result
        assert "@user1" in result
        assert "@user2" in result
        assert "owner" in result
        assert "member" in result

    @pytest.mark.asyncio
    async def test_list_members_success_with_slug(self, mock_client, mock_context):
        """Test member listing using slug attribute when user is not available."""
        mock_member = MagicMock()
        mock_member.slug = "member3"
        del mock_member.user
        del mock_member.role

        mock_result = MagicMock()
        mock_result.members = [mock_member]

        mock_client.organizations.list_members = AsyncMock(return_value=mock_result)

        result = await organizations.list_organization_members(org="myorg", ctx=mock_context)

        assert "@member3" in result
        assert "unknown" in result

    @pytest.mark.asyncio
    async def test_list_members_empty(self, mock_client, mock_context):
        """Test listing with no members."""
        mock_result = MagicMock()
        mock_result.members = []

        mock_client.organizations.list_members = AsyncMock(return_value=mock_result)

        result = await organizations.list_organization_members(org="myorg", ctx=mock_context)

        assert "No members found in organization 'myorg'" == result

    @pytest.mark.asyncio
    async def test_list_members_no_attr(self, mock_client, mock_context):
        """Test listing when result has no members attribute."""
        mock_result = MagicMock()
        del mock_result.members

        mock_client.organizations.list_members = AsyncMock(return_value=mock_result)

        result = await organizations.list_organization_members(org="myorg", ctx=mock_context)

        assert "No members found in organization 'myorg'" == result

    @pytest.mark.asyncio
    async def test_list_members_with_pagination(self, mock_client, mock_context):
        """Test listing with pagination."""
        mock_result = MagicMock()
        mock_result.members = []

        mock_client.organizations.list_members = AsyncMock(return_value=mock_result)

        await organizations.list_organization_members(
            org="myorg", page=2, per_page=10, ctx=mock_context
        )

        mock_client.organizations.list_members.assert_called_once_with(
            org="myorg", page=2, per_page=10
        )

    @pytest.mark.asyncio
    async def test_list_members_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.organizations.list_members = AsyncMock(side_effect=Exception("API Error"))

        result = await organizations.list_organization_members(org="myorg", ctx=mock_context)

        assert "Error listing organization members" in result


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
        organizations.register_tools(mock_mcp)

        assert mock_mcp.tool.call_count == 4

    @pytest.mark.asyncio
    async def test_register_tools_list_organizations(self) -> None:
        """Test that register_tools registers _list_organizations."""
        mock_mcp = MagicMock()
        mock_client = MagicMock()
        mock_context = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_client

        tool_calls: list[tuple[str, object]] = []

        def mock_tool(**kwargs: object) -> object:
            def decorator(func: object) -> object:
                tool_calls.append((getattr(func, "__name__", str(func)), func))
                return func

            return decorator

        mock_mcp.tool = mock_tool
        organizations.register_tools(mock_mcp)

        list_func = None
        for name, func in tool_calls:
            if name == "_list_organizations":
                list_func = func
                break

        assert list_func is not None

        mock_org = MagicMock()
        mock_org.slug = "testorg"
        mock_org.name = "Test Organization"

        mock_result = MagicMock()
        mock_result.organizations = [mock_org]

        mock_client.organizations.list = AsyncMock(return_value=mock_result)

        result = await list_func(page=1, per_page=30, ctx=mock_context)
        assert "Test Organization" in result

    @pytest.mark.asyncio
    async def test_register_tools_get_organization(self) -> None:
        """Test that register_tools registers _get_organization."""
        mock_mcp = MagicMock()
        mock_client = MagicMock()
        mock_context = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_client

        tool_calls: list[tuple[str, object]] = []

        def mock_tool(**kwargs: object) -> object:
            def decorator(func: object) -> object:
                tool_calls.append((getattr(func, "__name__", str(func)), func))
                return func

            return decorator

        mock_mcp.tool = mock_tool
        organizations.register_tools(mock_mcp)

        get_func = None
        for name, func in tool_calls:
            if name == "_get_organization":
                get_func = func
                break

        assert get_func is not None

        mock_org = MagicMock()
        mock_org.slug = "myorg"
        mock_org.name = "My Organization"
        mock_org.description = "A test org"
        mock_org.website = "https://example.com"
        mock_org.created_at = "2024-01-01"

        mock_client.organizations.get = AsyncMock(return_value=mock_org)

        result = await get_func(org="myorg", ctx=mock_context)
        assert "My Organization" in result

    @pytest.mark.asyncio
    async def test_register_tools_list_organization_repositories(self) -> None:
        """Test that register_tools registers _list_organization_repositories."""
        mock_mcp = MagicMock()
        mock_client = MagicMock()
        mock_context = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_client

        tool_calls: list[tuple[str, object]] = []

        def mock_tool(**kwargs: object) -> object:
            def decorator(func: object) -> object:
                tool_calls.append((getattr(func, "__name__", str(func)), func))
                return func

            return decorator

        mock_mcp.tool = mock_tool
        organizations.register_tools(mock_mcp)

        list_repos_func = None
        for name, func in tool_calls:
            if name == "_list_organization_repositories":
                list_repos_func = func
                break

        assert list_repos_func is not None

        mock_repo = MagicMock()
        mock_repo.slug = "test-repo"
        mock_repo.visibility = "public"
        mock_repo.description = "Test repo"

        mock_result = MagicMock()
        mock_result.repositories = [mock_repo]

        mock_client.organizations.list_repos = AsyncMock(return_value=mock_result)

        result = await list_repos_func(org="myorg", page=1, per_page=30, ctx=mock_context)
        assert "test-repo" in result

    @pytest.mark.asyncio
    async def test_register_tools_list_organization_members(self) -> None:
        """Test that register_tools registers _list_organization_members."""
        mock_mcp = MagicMock()
        mock_client = MagicMock()
        mock_context = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_client

        tool_calls: list[tuple[str, object]] = []

        def mock_tool(**kwargs: object) -> object:
            def decorator(func: object) -> object:
                tool_calls.append((getattr(func, "__name__", str(func)), func))
                return func

            return decorator

        mock_mcp.tool = mock_tool
        organizations.register_tools(mock_mcp)

        list_members_func = None
        for name, func in tool_calls:
            if name == "_list_organization_members":
                list_members_func = func
                break

        assert list_members_func is not None

        mock_member = MagicMock()
        mock_member.user = MagicMock()
        mock_member.user.slug = "testuser"
        mock_member.role = "owner"

        mock_result = MagicMock()
        mock_result.members = [mock_member]

        mock_client.organizations.list_members = AsyncMock(return_value=mock_result)

        result = await list_members_func(org="myorg", page=1, per_page=30, ctx=mock_context)
        assert "@testuser" in result
