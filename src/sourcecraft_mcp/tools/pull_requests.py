"""Pull request tools for SourceCraft MCP server."""

from __future__ import annotations

from mcp.server.fastmcp import Context
from pysourcecraft.models import (
    CreatePullRequestRequest,
    MergePullRequestRequest,
    PRState,
    UpdatePullRequestRequest,
)


def register_tools(mcp):
    """Register pull request tools with the MCP server."""

    @mcp.tool()
    async def list_pull_requests(
        owner: str,
        repo: str,
        status: str | None = None,
        author: str | None = None,
        source_branch: str | None = None,
        target_branch: str | None = None,
        page: int = 1,
        per_page: int = 30,
        ctx: Context = None,
    ) -> str:
        """List pull requests in a repository.

        Args:
            owner: Repository owner
            repo: Repository name
            status: Filter by status (draft, open, discarded, merging, merged)
            author: Filter by author username
            source_branch: Filter by source branch
            target_branch: Filter by target branch
            page: Page number
            per_page: Items per page
        """
        client = ctx.request_context.lifespan_context.client

        try:
            from pysourcecraft.models import PRFilters

            filters = PRFilters()
            if status:
                filters.state = PRState(status)
            if author:
                filters.author_id = author
            if source_branch:
                filters.source_branch = source_branch
            if target_branch:
                filters.target_branch = target_branch

            result = await client.pull_requests.list(
                owner=owner,
                repo=repo,
                filters=filters,
                page=page,
                per_page=per_page,
            )

            prs = result.data if hasattr(result, "data") else []
            if not prs:
                return f"No pull requests found in '{owner}/{repo}'"

            lines = [f"Pull Requests in '{owner}/{repo}':"]
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
                    f"   Author: @{pr.author.slug if pr.author else 'unknown'}"
                )

            return "\n\n".join(lines)
        except Exception as e:
            return f"Error listing pull requests: {e}"

    @mcp.tool()
    async def get_pull_request(
        owner: str,
        repo: str,
        pull_number: int,
        ctx: Context = None,
    ) -> str:
        """Get detailed information about a pull request.

        Args:
            owner: Repository owner
            repo: Repository name
            pull_number: Pull request number
        """
        client = ctx.request_context.lifespan_context.client

        try:
            result = await client.pull_requests.get(
                owner=owner,
                repo=repo,
                pull_number=pull_number,
            )

            status_icons = {
                "draft": "📝 Draft",
                "open": "🟢 Open",
                "discarded": "❌ Discarded",
                "merging": "🔄 Merging",
                "merged": "✅ Merged",
            }
            status_display = status_icons.get(result.status, result.status)

            lines = [
                f"#{result.slug}: {result.title}",
                f"Status: {status_display}",
                f"Author: @{result.author.slug if result.author else 'unknown'}",
                f"Source: {result.source_branch}",
                f"Target: {result.target_branch}",
            ]

            if result.description:
                lines.append(f"\nDescription:\n{result.description}")

            if result.merge_info:
                if result.merge_info.merge_commit_hash:
                    lines.append(f"\nMerge Commit: {result.merge_info.merge_commit_hash[:7]}")
                if result.merge_info.error:
                    lines.append(f"Merge Error: {result.merge_info.error}")

            lines.extend(
                [
                    f"\nCreated: {result.created_at}",
                    f"Updated: {result.updated_at}",
                ]
            )

            return "\n".join(lines)
        except Exception as e:
            return f"Error getting pull request: {e}"

    @mcp.tool()
    async def create_pull_request(
        owner: str,
        repo: str,
        title: str,
        source_branch: str,
        target_branch: str,
        description: str = "",
        reviewer_ids: list[str] | None = None,
        publish: bool = False,
        ctx: Context = None,
    ) -> str:
        """Create a new pull request.

        Args:
            owner: Repository owner
            repo: Repository name
            title: PR title
            source_branch: Source branch name
            target_branch: Target branch name
            description: PR description
            reviewer_ids: List of user IDs to assign as reviewers
            publish: Whether to publish immediately (False = draft)
        """
        client = ctx.request_context.lifespan_context.client

        try:
            request = CreatePullRequestRequest(
                title=title,
                source_branch=source_branch,
                target_branch=target_branch,
                description=description or None,
                reviewer_ids=reviewer_ids or None,
                publish=publish,
            )

            result = await client.pull_requests.create(
                owner=owner,
                repo=repo,
                request=request,
            )

            status = "published" if publish else "draft"
            return (
                f"Pull request created as {status}!\n\n"
                f"#{result.slug}: {result.title}\n"
                f"Branch: {result.source_branch} → {result.target_branch}\n"
                f"Author: @{result.author.slug if result.author else 'unknown'}"
            )
        except Exception as e:
            return f"Error creating pull request: {e}"

    @mcp.tool()
    async def update_pull_request(
        owner: str,
        repo: str,
        pull_number: int,
        title: str | None = None,
        description: str | None = None,
        ctx: Context = None,
    ) -> str:
        """Update a pull request.

        Args:
            owner: Repository owner
            repo: Repository name
            pull_number: Pull request number
            title: New title (optional)
            description: New description (optional)
        """
        client = ctx.request_context.lifespan_context.client

        try:
            request = UpdatePullRequestRequest()
            if title is not None:
                request.title = title
            if description is not None:
                request.description = description

            result = await client.pull_requests.update(
                owner=owner,
                repo=repo,
                pull_number=pull_number,
                request=request,
            )

            return f"Pull request updated!\n\n#{result.slug}: {result.title}"
        except Exception as e:
            return f"Error updating pull request: {e}"

    @mcp.tool()
    async def merge_pull_request(
        owner: str,
        repo: str,
        pull_number: int,
        commit_title: str = "",
        commit_message: str = "",
        squash: bool = False,
        delete_branch: bool = False,
        ctx: Context = None,
    ) -> str:
        """Merge a pull request.

        Args:
            owner: Repository owner
            repo: Repository name
            pull_number: Pull request number
            commit_title: Custom merge commit title
            commit_message: Custom merge commit message
            squash: Whether to squash commits
            delete_branch: Whether to delete source branch after merge
        """
        client = ctx.request_context.lifespan_context.client

        from pysourcecraft.models import PRMergeMethod

        try:
            request = MergePullRequestRequest(
                commit_title=commit_title or None,
                commit_message=commit_message or None,
                method=PRMergeMethod.SQUASH if squash else PRMergeMethod.MERGE,
            )

            result = await client.pull_requests.merge(
                owner=owner,
                repo=repo,
                pull_number=pull_number,
                request=request,
            )

            if result.merge_info and result.merge_info.merge_commit_hash:
                return (
                    f"Pull request #{pull_number} merged successfully!\n"
                    f"Merge commit: {result.merge_info.merge_commit_hash[:7]}"
                )
            return f"Pull request #{pull_number} merged successfully!"
        except Exception as e:
            return f"Error merging pull request: {e}"

    @mcp.tool()
    async def publish_pull_request(
        owner: str,
        repo: str,
        pull_number: int,
        ctx: Context = None,
    ) -> str:
        """Publish a draft pull request (change status to open).

        Args:
            owner: Repository owner
            repo: Repository name
            pull_number: Pull request number
        """
        client = ctx.request_context.lifespan_context.client

        try:
            result = await client.pull_requests.publish(
                owner=owner,
                repo=repo,
                pull_number=pull_number,
            )
            return f"Pull request #{pull_number} published! Status: {result.status}"
        except Exception as e:
            return f"Error publishing pull request: {e}"

    @mcp.tool()
    async def discard_pull_request(
        owner: str,
        repo: str,
        pull_number: int,
        ctx: Context = None,
    ) -> str:
        """Discard (close) a pull request.

        Args:
            owner: Repository owner
            repo: Repository name
            pull_number: Pull request number
        """
        client = ctx.request_context.lifespan_context.client

        try:
            result = await client.pull_requests.discard(
                owner=owner,
                repo=repo,
                pull_number=pull_number,
            )
            return f"Pull request #{pull_number} discarded. Status: {result.status}"
        except Exception as e:
            return f"Error discarding pull request: {e}"

    @mcp.tool()
    async def list_pr_reviewers(
        owner: str,
        repo: str,
        pull_number: int,
        ctx: Context = None,
    ) -> str:
        """List reviewers for a pull request.

        Args:
            owner: Repository owner
            repo: Repository name
            pull_number: Pull request number
        """
        client = ctx.request_context.lifespan_context.client

        try:
            result = await client.pull_requests.list_reviewers(
                owner=owner,
                repo=repo,
                pull_number=pull_number,
            )

            reviewers = result.reviewers if hasattr(result, "reviewers") else []
            if not reviewers:
                return f"No reviewers assigned to PR #{pull_number}"

            lines = [f"Reviewers for PR #{pull_number} in '{owner}/{repo}':"]
            for reviewer in reviewers:
                decision = reviewer.review_decision or "no decision"
                decision_icon = {
                    "approve": "✅",
                    "trust": "🤝",
                    "block": "🚫",
                    "abstain": "➖",
                }.get(decision, "⏳")
                lines.append(f"{decision_icon} @{reviewer.user.slug} - {decision}")

            return "\n".join(lines)
        except Exception as e:
            return f"Error listing reviewers: {e}"

    @mcp.tool()
    async def add_pr_reviewer(
        owner: str,
        repo: str,
        pull_number: int,
        user_id: str,
        ctx: Context = None,
    ) -> str:
        """Add a reviewer to a pull request.

        Args:
            owner: Repository owner
            repo: Repository name
            pull_number: Pull request number
            user_id: User ID to add as reviewer
        """
        client = ctx.request_context.lifespan_context.client

        try:
            await client.pull_requests.add_reviewer(
                owner=owner,
                repo=repo,
                pull_number=pull_number,
                user_id=user_id,
            )
            return f"Reviewer added to PR #{pull_number}"
        except Exception as e:
            return f"Error adding reviewer: {e}"

    @mcp.tool()
    async def set_review_decision(
        owner: str,
        repo: str,
        pull_number: int,
        decision: str,
        ctx: Context = None,
    ) -> str:
        """Set your review decision on a pull request.

        Args:
            owner: Repository owner
            repo: Repository name
            pull_number: Pull request number
            decision: Review decision (approve, trust, block, abstain)
        """
        client = ctx.request_context.lifespan_context.client

        try:
            await client.pull_requests.set_review_decision(
                owner=owner,
                repo=repo,
                pull_number=pull_number,
                decision=decision,
            )
            return f"Review decision '{decision}' set on PR #{pull_number}"
        except Exception as e:
            return f"Error setting review decision: {e}"
