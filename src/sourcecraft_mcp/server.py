"""SourceCraft MCP Server.

Main entry point for the MCP server providing SourceCraft API integration.
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator

from mcp.server.fastmcp import FastMCP
from pysourcecraft import SourceCraftClient

from sourcecraft_mcp.tools import (
    cicd_tools,
    issues_tools,
    organizations_tools,
    pull_requests_tools,
    releases_tools,
    repositories_tools,
    users_tools,
)


@dataclass
class AppContext:
    """Application context containing the SourceCraft client."""

    client: SourceCraftClient


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle.

    Initialize the SourceCraft client on startup and cleanup on shutdown.
    """
    api_token = os.environ.get("SOURCECRAFT_API_TOKEN")
    base_url = os.environ.get("SOURCECRAFT_BASE_URL", "https://api.sourcecraft.tech")

    if not api_token:
        raise ValueError(
            "SOURCECRAFT_API_TOKEN environment variable is required. "
            "Please set it to your SourceCraft API token."
        )

    client = SourceCraftClient(api_token=api_token, base_url=base_url)

    try:
        yield AppContext(client=client)
    finally:
        # Cleanup if needed
        pass


# Create the MCP server
mcp = FastMCP(
    "sourcecraft-mcp",
    lifespan=app_lifespan,
    instructions="""
SourceCraft MCP Server provides tools for interacting with SourceCraft platform.

Available tools cover:
- Repositories: list, get, create, update, delete, branches, tags, file tree
- Issues: list, get, create, update, delete, comments, labels, linked issues
- Pull Requests: list, get, create, update, merge, publish, comments, reviewers
- CI/CD: list runs, get run details, logs, artifacts, trigger workflows
- Releases: list, get, create, update, publish, upload assets
- Users: get current user, get user profile, list my issues
- Organizations: list, get, list repos, manage invites

All tools require SOURCECRAFT_API_TOKEN environment variable to be set.
""",
)


# Register all tools
repositories_tools.register_tools(mcp)
issues_tools.register_tools(mcp)
pull_requests_tools.register_tools(mcp)
cicd_tools.register_tools(mcp)
releases_tools.register_tools(mcp)
users_tools.register_tools(mcp)
organizations_tools.register_tools(mcp)


def main():
    """Main entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
