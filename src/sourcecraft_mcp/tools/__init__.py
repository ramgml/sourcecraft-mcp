"""SourceCraft MCP tools package."""

from sourcecraft_mcp.tools import (
    repositories,
    issues,
    pull_requests,
    cicd,
    releases,
    users,
    organizations,
)

repositories_tools = repositories
issues_tools = issues
pull_requests_tools = pull_requests
cicd_tools = cicd
releases_tools = releases
users_tools = users
organizations_tools = organizations

__all__ = [
    "repositories_tools",
    "issues_tools",
    "pull_requests_tools",
    "cicd_tools",
    "releases_tools",
    "users_tools",
    "organizations_tools",
]
