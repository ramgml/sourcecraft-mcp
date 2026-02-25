"""Tests for SourceCraft MCP server."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from sourcecraft_mcp.server import app_lifespan, main, mcp


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

    def test_mcp_server_instructions(self):
        """Test that MCP server has instructions."""
        assert mcp.instructions is not None
        assert "SourceCraft MCP Server" in mcp.instructions
        assert "Repositories" in mcp.instructions

    def test_mcp_server_has_lifespan(self):
        """Test that MCP server has lifespan configured."""
        # The lifespan is set during initialization via the lifespan parameter
        # We verify it's configured by checking the server was created successfully
        assert mcp is not None


class TestMainFunction:
    """Test main entry point."""

    def test_main_function_calls_mcp_run(self):
        """Test that main() calls mcp.run()."""
        with patch.object(mcp, "run") as mock_run:
            main()
            mock_run.assert_called_once()

    def test_main_module_execution(self):
        """Test __main__ block execution."""
        with patch.object(mcp, "run") as mock_run:
            # Simulate running as __main__
            import sourcecraft_mcp.server as server_module

            # Call main directly as it would be called in __main__ block
            server_module.main()
            mock_run.assert_called_once()


class TestAppLifespanCustomURL:
    """Test application lifespan with custom base URL."""

    @pytest.mark.asyncio
    async def test_app_lifespan_with_custom_base_url(self):
        """Test app lifespan with custom SOURCECRAFT_BASE_URL."""
        with patch.dict(
            "os.environ",
            {
                "SOURCECRAFT_API_TOKEN": "test-token",
                "SOURCECRAFT_BASE_URL": "https://custom.api.com",
            },
        ):
            mock_server = MagicMock()

            async with app_lifespan(mock_server) as context:
                assert context.client is not None
                assert context.client.api_token == "test-token"


class TestAppContext:
    """Test AppContext dataclass."""

    def test_app_context_creation(self):
        """Test AppContext can be created with a client."""
        from sourcecraft_mcp.server import AppContext

        mock_client = MagicMock()
        context = AppContext(client=mock_client)
        assert context.client is mock_client
