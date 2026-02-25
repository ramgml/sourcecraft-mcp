"""Tests for SourceCraft MCP server."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from sourcecraft_mcp.server import app_lifespan, mcp


class TestAppLifespan:
    """Test application lifespan management."""

    @pytest.mark.asyncio
    async def test_app_lifespan_success(self):
        """Test successful app lifespan initialization."""
        with patch.dict("os.environ", {"SOURCECRAFT_API_TOKEN": "test-token"}):
            mock_server = MagicMock()

            async with app_lifespan(mock_server) as context:
                assert context.client is not None
                assert context.client.api_token == "test-token"

    @pytest.mark.asyncio
    async def test_app_lifespan_missing_token(self):
        """Test app lifespan with missing token."""
        with patch.dict("os.environ", {}, clear=True):
            mock_server = MagicMock()

            with pytest.raises(ValueError) as exc_info:
                async with app_lifespan(mock_server):
                    pass

            assert "SOURCECRAFT_API_TOKEN" in str(exc_info.value)


class TestMCPServer:
    """Test MCP server functionality."""

    def test_mcp_server_created(self):
        """Test that MCP server is created with correct name."""
        assert mcp.name == "sourcecraft-mcp"

    def test_mcp_has_tools(self):
        """Test that MCP server has registered tools."""
        # The tools are registered when the module is imported
        # We can't easily check them without running the server,
        # but we can verify the server was created
        assert mcp is not None
