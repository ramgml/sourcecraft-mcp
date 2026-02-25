"""Issue tools for SourceCraft MCP server."""

from __future__ import annotations

from mcp.server.fastmcp import Context
from pysourcecraft.models import (
    CreateIssueRequest,
    Priority,
    UpdateIssueRequest,
)


def register_tools(mcp):
    """Register issue tools with the MCP server."""

    @mcp.tool()
    async def list_issues(
        owner: str,
        repo: str,
        status: str | None = None,
        priority: str | None = None,
        assignee: str | None = None,
        label: str | None = None,
        page: int = 1,
        per_page: int = 30,
        ctx: Context = None,
    ) -> str:
        """List issues in a repository.

        Args:
            owner: Repository owner
            repo: Repository name
            status: Filter by status (open, inProgress, paused, closed, etc.)
            priority: Filter by priority (trivial, minor, normal, critical, blocker)
            assignee: Filter by assignee username
            label: Filter by label slug
            page: Page number
            per_page: Items per page
        """
        client = ctx.request_context.lifespan_context.client

        try:
            from pysourcecraft.models import IssueFilters

            filters = IssueFilters()
            if status:
                filters.status = status
            if priority:
                filters.priority = priority
            if assignee:
                filters.assignee_slug = assignee
            if label:
                filters.label_slug = label

            result = await client.issues.list(
                owner=owner,
                repo=repo,
                filters=filters,
                page=page,
                per_page=per_page,
            )

            issues = result.data if hasattr(result, "data") else []
            if not issues:
                return f"No issues found in '{owner}/{repo}'"

            lines = [f"Issues in '{owner}/{repo}':"]
            for issue in issues:
                status_icon = (
                    "🟢"
                    if issue.status.slug == "open"
                    else "🔴"
                    if issue.status.slug == "closed"
                    else "🟡"
                )
                assignee_info = f" @{issue.assignee.slug}" if issue.assignee else " (unassigned)"
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
                    f"{status_icon} #{issue.slug} {priority_icon}{issue.title}{assignee_info}\n"
                    f"   Status: {issue.status.name} | Priority: {issue.priority or 'normal'}"
                )

            return "\n\n".join(lines)
        except Exception as e:
            return f"Error listing issues: {e}"

    @mcp.tool()
    async def get_issue(
        owner: str,
        repo: str,
        issue_number: int,
        ctx: Context = None,
    ) -> str:
        """Get detailed information about an issue.

        Args:
            owner: Repository owner
            repo: Repository name
            issue_number: Issue number
        """
        client = ctx.request_context.lifespan_context.client

        try:
            result = await client.issues.get(
                owner=owner,
                repo=repo,
                issue_number=issue_number,
            )

            status_icon = (
                "🟢"
                if result.status.slug == "open"
                else "🔴"
                if result.status.slug == "closed"
                else "🟡"
            )

            lines = [
                f"{status_icon} Issue #{result.slug}: {result.title}",
                f"Description: {result.description or 'No description'}",
                f"Status: {result.status.name}",
                f"Priority: {result.priority or 'normal'}",
                f"Author: @{result.author.slug if result.author else 'unknown'}",
            ]

            if result.assignee:
                lines.append(f"Assignee: @{result.assignee.slug}")

            if result.labels:
                label_names = [label.name for label in result.labels]
                lines.append(f"Labels: {', '.join(label_names)}")

            if result.milestone:
                lines.append(f"Milestone: {result.milestone.slug}")

            if result.deadline:
                lines.append(f"Deadline: {result.deadline}")

            if result.linked_prs:
                pr_links = [f"#{pr.slug}" for pr in result.linked_prs]
                lines.append(f"Linked PRs: {', '.join(pr_links)}")

            lines.extend(
                [
                    f"Created: {result.created_at}",
                    f"Updated: {result.updated_at}",
                ]
            )

            return "\n".join(lines)
        except Exception as e:
            return f"Error getting issue: {e}"

    @mcp.tool()
    async def create_issue(
        owner: str,
        repo: str,
        title: str,
        description: str = "",
        priority: str = "normal",
        assignee_id: str = "",
        label_slugs: list[str] | None = None,
        ctx: Context = None,
    ) -> str:
        """Create a new issue in a repository.

        Args:
            owner: Repository owner
            repo: Repository name
            title: Issue title
            description: Issue description
            priority: Issue priority (trivial, minor, normal, critical, blocker)
            assignee_id: User ID to assign the issue to
            label_slugs: List of label slugs to apply
        """
        client = ctx.request_context.lifespan_context.client

        try:
            request = CreateIssueRequest(
                title=title,
                description=description or None,
                priority=Priority(priority) if priority else None,
                assignee_id=assignee_id or None,
                label_slugs=label_slugs or None,
            )

            result = await client.issues.create(
                owner=owner,
                repo=repo,
                request=request,
            )

            return (
                f"Issue created successfully!\n\n"
                f"Issue #{result.slug}: {result.title}\n"
                f"Status: {result.status.name}\n"
                f"Priority: {result.priority or 'normal'}\n"
                f"Author: @{result.author.slug if result.author else 'unknown'}"
            )
        except Exception as e:
            return f"Error creating issue: {e}"

    @mcp.tool()
    async def update_issue(
        owner: str,
        repo: str,
        issue_number: int,
        title: str | None = None,
        description: str | None = None,
        status_slug: str | None = None,
        priority: str | None = None,
        assignee_id: str | None = None,
        ctx: Context = None,
    ) -> str:
        """Update an existing issue.

        Args:
            owner: Repository owner
            repo: Repository name
            issue_number: Issue number
            title: New title (optional)
            description: New description (optional)
            status_slug: New status slug (open, inProgress, paused, closed, etc.)
            priority: New priority (trivial, minor, normal, critical, blocker)
            assignee_id: New assignee ID (empty string to unassign)
        """
        client = ctx.request_context.lifespan_context.client

        try:
            request = UpdateIssueRequest()
            if title is not None:
                request.title = title
            if description is not None:
                request.description = description or None
            if status_slug is not None:
                request.status_slug = status_slug
            if priority is not None:
                request.priority = Priority(priority)
            if assignee_id is not None:
                request.assignee_id = assignee_id if assignee_id else None

            result = await client.issues.update(
                owner=owner,
                repo=repo,
                issue_number=issue_number,
                request=request,
            )

            return (
                f"Issue updated successfully!\n\n"
                f"Issue #{result.slug}: {result.title}\n"
                f"Status: {result.status.name}\n"
                f"Priority: {result.priority or 'normal'}"
            )
        except Exception as e:
            return f"Error updating issue: {e}"

    @mcp.tool()
    async def close_issue(
        owner: str,
        repo: str,
        issue_number: int,
        ctx: Context = None,
    ) -> str:
        """Close an issue.

        Args:
            owner: Repository owner
            repo: Repository name
            issue_number: Issue number
        """
        client = ctx.request_context.lifespan_context.client

        try:
            await client.issues.close(
                owner=owner,
                repo=repo,
                issue_number=issue_number,
            )
            return f"Issue #{issue_number} in '{owner}/{repo}' closed successfully"
        except Exception as e:
            return f"Error closing issue: {e}"

    @mcp.tool()
    async def reopen_issue(
        owner: str,
        repo: str,
        issue_number: int,
        ctx: Context = None,
    ) -> str:
        """Reopen a closed issue.

        Args:
            owner: Repository owner
            repo: Repository name
            issue_number: Issue number
        """
        client = ctx.request_context.lifespan_context.client

        try:
            await client.issues.reopen(
                owner=owner,
                repo=repo,
                issue_number=issue_number,
            )
            return f"Issue #{issue_number} in '{owner}/{repo}' reopened successfully"
        except Exception as e:
            return f"Error reopening issue: {e}"

    @mcp.tool()
    async def list_issue_comments(
        owner: str,
        repo: str,
        issue_number: int,
        page: int = 1,
        per_page: int = 30,
        ctx: Context = None,
    ) -> str:
        """List comments on an issue.

        Args:
            owner: Repository owner
            repo: Repository name
            issue_number: Issue number
            page: Page number
            per_page: Items per page
        """
        client = ctx.request_context.lifespan_context.client

        try:
            result = await client.issues.list_comments(
                owner=owner,
                repo=repo,
                issue_number=issue_number,
                page=page,
                per_page=per_page,
            )

            comments = result.data if hasattr(result, "data") else []
            if not comments:
                return f"No comments on issue #{issue_number}"

            lines = [f"Comments on issue #{issue_number} in '{owner}/{repo}':"]
            for comment in comments:
                author = f"@{comment.author.slug}" if comment.author else "unknown"
                lines.append(f"\n{author} at {comment.created_at}:\n{comment.body}")

            return "\n".join(lines)
        except Exception as e:
            return f"Error listing comments: {e}"

    @mcp.tool()
    async def add_issue_comment(
        owner: str,
        repo: str,
        issue_number: int,
        body: str,
        ctx: Context = None,
    ) -> str:
        """Add a comment to an issue.

        Args:
            owner: Repository owner
            repo: Repository name
            issue_number: Issue number
            body: Comment text
        """
        client = ctx.request_context.lifespan_context.client

        try:
            result = await client.issues.create_comment(
                owner=owner,
                repo=repo,
                issue_number=issue_number,
                body=body,
            )

            author = result.author.slug if result.author else 'unknown'
            return f"Comment added to issue #{issue_number} by @{author}"
        except Exception as e:
            return f"Error adding comment: {e}"
