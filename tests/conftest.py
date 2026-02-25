"""Test configuration for SourceCraft MCP server."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def mock_client():
    """Create a mock SourceCraft client."""
    client = MagicMock()

    # Mock all subclients
    client.repositories = AsyncMock()
    client.issues = AsyncMock()
    client.pull_requests = AsyncMock()
    client.cicd = AsyncMock()
    client.releases = AsyncMock()
    client.users = AsyncMock()
    client.organizations = AsyncMock()

    return client


@pytest.fixture
def mock_context(mock_client):
    """Create a mock MCP context."""
    context = MagicMock()
    context.request_context.lifespan_context.client = mock_client
    return context
