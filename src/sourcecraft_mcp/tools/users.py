"""User tools for SourceCraft MCP server."""

from __future__ import annotations

from mcp.server.fastmcp import Context


def register_tools(mcp):
    """Register user tools with the MCP server."""

    @mcp.tool()
    async def get_current_user(
        ctx: Context = None,
    ) -> str:
        """Get information about the currently authenticated user."""
        client = ctx.request_context.lifespan_context.client

        try:
            result = await client.users.get_current()

            lines = [
                f"👤 User: {result.display_name or result.username}",
                f"Username: @{result.username}",
            ]

            if result.bio:
                lines.append(f"Bio: {result.bio}")

            if result.location:
                loc_parts = []
                if result.location.city:
                    loc_parts.append(result.location.city)
                if result.location.country:
                    loc_parts.append(result.location.country)
                if loc_parts:
                    lines.append(f"Location: {', '.join(loc_parts)}")

            if result.workplace:
                if result.workplace.company:
                    lines.append(f"Company: {result.workplace.company}")
                if result.workplace.position:
                    lines.append(f"Position: {result.workplace.position}")

            if result.links:
                lines.append(f"Links: {len(result.links)}")

            lines.append(f"Visibility: {result.visibility}")

            return "\n".join(lines)
        except Exception as e:
            return f"Error getting current user: {e}"

    @mcp.tool()
    async def get_user(
        username: str,
        ctx: Context = None,
    ) -> str:
        """Get information about a user by username.

        Args:
            username: Username to look up
        """
        client = ctx.request_context.lifespan_context.client

        try:
            result = await client.users.get(username=username)

            lines = [
                f"👤 User: {result.display_name or result.username}",
                f"Username: @{result.username}",
            ]

            if result.bio:
                lines.append(f"Bio: {result.bio}")

            if result.location:
                loc_parts = []
                if result.location.city:
                    loc_parts.append(result.location.city)
                if result.location.country:
                    loc_parts.append(result.location.country)
                if loc_parts:
                    lines.append(f"Location: {', '.join(loc_parts)}")

            if result.workplace:
                if result.workplace.company:
                    lines.append(f"Company: {result.workplace.company}")
                if result.workplace.position:
                    lines.append(f"Position: {result.workplace.position}")

            return "\n".join(lines)
        except Exception as e:
            return f"Error getting user: {e}"

    @mcp.tool()
    async def list_my_issues(
        page_size: int = 30,
        page_token: str = "",
        ctx: Context = None,
    ) -> str:
        """List issues assigned to or created by the authenticated user.

        Args:
            page_size: Maximum number of issues to return
            page_token: Token for pagination
        """
        client = ctx.request_context.lifespan_context.client

        try:
            result = await client.users.list_my_issues(
                page_size=page_size,
                page_token=page_token or None,
            )

            issues = result.issues if hasattr(result, "issues") else []
            if not issues:
                return "No issues found for you"

            lines = [f"Your issues ({len(issues)}):"]
            for issue in issues:
                status_icon = "🟢" if issue.status.slug == "open" else "🔴"
                priority_icon = ""
                if issue.priority:
                    priority_map = {
                        "trivial": "🔹",
                        "minor": "🔸",
                        "normal": "",
                        "critical": "⚠️",
                        "blocker": "🚫",
                    }
                    priority_icon = priority_map.get(issue.priority, "")

                lines.append(
                    f"{status_icon} #{issue.slug} {priority_icon}{issue.title}\n"
                    f"   Status: {issue.status.name} | Priority: {issue.priority or 'normal'}"
                )

            return "\n\n".join(lines)
        except Exception as e:
            return f"Error listing my issues: {e}"

    @mcp.tool()
    async def list_user_pull_requests(
        username: str,
        role: str = "any",
        page_size: int = 30,
        page_token: str = "",
        ctx: Context = None,
    ) -> str:
        """List pull requests for a user.

        Args:
            username: Username to look up PRs for
            role: Role filter (author, reviewer, any)
            page_size: Maximum number of PRs to return
            page_token: Token for pagination
        """
        client = ctx.request_context.lifespan_context.client

        try:
            result = await client.users.list_pull_requests(
                username=username,
                role=role,
                page_size=page_size,
                page_token=page_token or None,
            )

            prs = result.pull_requests if hasattr(result, "pull_requests") else []
            if not prs:
                return f"No pull requests found for @{username}"

            lines = [f"Pull requests for @{username} (role: {role}):"]
            for pr in prs:
                status_icons = {
                    "draft": "📝",
                    "open": "🟢",
                    "discarded": "❌",
                    "merging": "🔄",
                    "merged": "✅",
                }
                icon = status_icons.get(pr.status, "❓")

                lines.append(
                    f"{icon} #{pr.slug}: {pr.title}\n"
                    f"   Branch: {pr.source_branch} → {pr.target_branch}\n"
                    f"   Status: {pr.status}"
                )

            return "\n\n".join(lines)
        except Exception as e:
            return f"Error listing user pull requests: {e}"
