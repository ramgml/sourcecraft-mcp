"""Tests for repository tools."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

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
        mock_client.repositories.list = AsyncMock(
            side_effect=Exception("API Error")
        )
        
        result = await repositories.list_repositories(ctx=mock_context)
        
        assert "Error listing repositories" in result


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
        mock_repo.counters = MagicMock(
            forks="10",
            pull_requests="5",
            issues="3"
        )
        mock_repo.clone_url = MagicMock(
            ssh="git@sourcecraft.dev:test/test-repo.git",
            https="https://sourcecraft.dev/test/test-repo.git"
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
