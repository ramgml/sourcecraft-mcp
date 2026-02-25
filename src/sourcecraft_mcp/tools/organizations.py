"""Organization tools for SourceCraft MCP server."""

from __future__ import annotations

from mcp.server.fastmcp import Context


def register_tools(mcp):
    """Register organization tools with the MCP server."""

    @mcp.tool()
    async def list_organizations(
        page: int = 1,
        per_page: int = 30,
        ctx: Context = None,
    ) -> str:
        """List organizations.

        Args:
            page: Page number
            per_page: Items per page
        """
        client = ctx.request_context.lifespan_context.client

        try:
            result = await client.organizations.list(
                page=page,
                per_page=per_page,
            )

            orgs = result.organizations if hasattr(result, "organizations") else []
            if not orgs:
                return "No organizations found"

            lines = [f"Organizations ({len(orgs)}):"]
            for org in orgs:
                lines.append(f"🏢 {org.slug}\n   Name: {org.name or 'N/A'}")

            return "\n\n".join(lines)
        except Exception as e:
            return f"Error listing organizations: {e}"

    @mcp.tool()
    async def get_organization(
        org: str,
        ctx: Context = None,
    ) -> str:
        """Get information about an organization.

        Args:
            org: Organization slug
        """
        client = ctx.request_context.lifespan_context.client

        try:
            result = await client.organizations.get(org=org)

            lines = [
                f"🏢 Organization: {result.slug}",
                f"Name: {result.name or 'N/A'}",
            ]

            if hasattr(result, "description") and result.description:
                lines.append(f"Description: {result.description}")

            if hasattr(result, "website") and result.website:
                lines.append(f"Website: {result.website}")

            if hasattr(result, "created_at") and result.created_at:
                lines.append(f"Created: {result.created_at}")

            return "\n".join(lines)
        except Exception as e:
            return f"Error getting organization: {e}"

    @mcp.tool()
    async def list_organization_repositories(
        org: str,
        page: int = 1,
        per_page: int = 30,
        ctx: Context = None,
    ) -> str:
        """List repositories in an organization.

        Args:
            org: Organization slug
            page: Page number
            per_page: Items per page
        """
        client = ctx.request_context.lifespan_context.client

        try:
            result = await client.organizations.list_repos(
                org=org,
                page=page,
                per_page=per_page,
            )

            repos = result.repositories if hasattr(result, "repositories") else []
            if not repos:
                return f"No repositories found in organization '{org}'"

            lines = [f"Repositories in '{org}' ({len(repos)}):"]
            for repo in repos:
                visibility = "📦" if repo.visibility == "public" else "🔒"
                lines.append(
                    f"{visibility} {repo.slug}\n"
                    f"   Description: {repo.description or 'No description'}"
                )

            return "\n\n".join(lines)
        except Exception as e:
            return f"Error listing organization repositories: {e}"

    @mcp.tool()
    async def list_organization_members(
        org: str,
        page: int = 1,
        per_page: int = 30,
        ctx: Context = None,
    ) -> str:
        """List members of an organization.

        Args:
            org: Organization slug
            page: Page number
            per_page: Items per page
        """
        client = ctx.request_context.lifespan_context.client

        try:
            result = await client.organizations.list_members(
                org=org,
                page=page,
                per_page=per_page,
            )

            members = result.members if hasattr(result, "members") else []
            if not members:
                return f"No members found in organization '{org}'"

            lines = [f"Members of '{org}' ({len(members)}):"]
            for member in members:
                role = member.role if hasattr(member, "role") else "unknown"
                lines.append(
                    f"👤 @{member.user.slug if hasattr(member, 'user') else member.slug} - {role}"
                )

            return "\n".join(lines)
        except Exception as e:
            return f"Error listing organization members: {e}"
