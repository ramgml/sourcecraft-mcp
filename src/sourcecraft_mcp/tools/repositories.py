"""Repository tools for SourceCraft MCP server."""

from __future__ import annotations

from mcp.server.fastmcp import Context
from pysourcecraft.models import CreateRepositoryRequest, RepoVisibility, UpdateRepositoryRequest


def register_tools(mcp):
    """Register repository tools with the MCP server."""

    @mcp.tool()
    async def list_repositories(
        username: str | None = None,
        page: int = 1,
        per_page: int = 30,
        ctx: Context | None = None,
    ) -> str:
        """List repositories for a user or the authenticated user.

        Args:
            username: Username to list repos for (None for authenticated user)
            page: Page number
            per_page: Items per page
        """
        assert ctx is not None
        client = ctx.request_context.lifespan_context.client

        try:
            result = await client.repositories.list(
                username=username,
                page=page,
                per_page=per_page,
            )

            repos = result.repositories if hasattr(result, "repositories") else []
            if not repos:
                return "No repositories found"

            lines = [f"Found {len(repos)} repositories:"]
            for repo in repos:
                visibility = "📦" if repo.visibility == "public" else "🔒"
                lines.append(
                    f"{visibility} {repo.slug} - {repo.name}\n"
                    f"  Description: {repo.description or 'No description'}\n"
                    f"  Language: {repo.language.name if repo.language else 'Unknown'}\n"
                    f"  Updated: {repo.last_updated}"
                )

            if hasattr(result, "next_page_token") and result.next_page_token:
                lines.append(f"\n(More results available, use page={page + 1})")

            return "\n\n".join(lines)
        except Exception as e:
            return f"Error listing repositories: {e}"

    @mcp.tool()
    async def list_organization_repositories(
        org: str,
        page: int = 1,
        per_page: int = 30,
        ctx: Context | None = None,
    ) -> str:
        """List repositories in an organization.

        Args:
            org: Organization name
            page: Page number
            per_page: Items per page
        """
        assert ctx is not None
        client = ctx.request_context.lifespan_context.client

        try:
            result = await client.repositories.list_org_repos(
                org=org,
                page=page,
                per_page=per_page,
            )

            repos = result.repositories if hasattr(result, "repositories") else []
            if not repos:
                return f"No repositories found in organization '{org}'"

            lines = [f"Found {len(repos)} repositories in '{org}':"]
            for repo in repos:
                visibility = "📦" if repo.visibility == "public" else "🔒"
                lines.append(
                    f"{visibility} {repo.slug} - {repo.name}\n"
                    f"  Description: {repo.description or 'No description'}"
                )

            return "\n\n".join(lines)
        except Exception as e:
            return f"Error listing organization repositories: {e}"

    @mcp.tool()
    async def get_repository(
        owner: str,
        repo: str,
        ctx: Context | None = None,
    ) -> str:
        """Get detailed information about a repository.

        Args:
            owner: Repository owner
            repo: Repository name
        """
        assert ctx is not None
        client = ctx.request_context.lifespan_context.client

        try:
            result = await client.repositories.get(owner=owner, repo=repo)

            visibility = "📦 Public" if result.visibility == "public" else "🔒 Private"

            lines = [
                f"Repository: {result.slug}",
                f"Name: {result.name}",
                f"Visibility: {visibility}",
                f"Description: {result.description or 'No description'}",
                f"Default Branch: {result.default_branch}",
                f"Empty: {'Yes' if result.is_empty else 'No'}",
            ]

            if result.language:
                lines.append(f"Language: {result.language.name}")

            if result.counters:
                lines.append(
                    f"Counters: {result.counters.forks} forks, "
                    f"{result.counters.pull_requests} PRs, "
                    f"{result.counters.issues} issues"
                )

            lines.extend(
                [
                    f"Web URL: {result.web_url}",
                    f"Clone (SSH): {result.clone_url.ssh if result.clone_url else 'N/A'}",
                    f"Clone (HTTPS): {result.clone_url.https if result.clone_url else 'N/A'}",
                    f"Last Updated: {result.last_updated}",
                ]
            )

            return "\n".join(lines)
        except Exception as e:
            return f"Error getting repository: {e}"

    @mcp.tool()
    async def create_repository(
        name: str,
        description: str = "",
        visibility: str = "private",
        ctx: Context | None = None,
    ) -> str:
        """Create a new repository for the authenticated user.

        Args:
            name: Repository name
            description: Repository description
            visibility: Repository visibility (public, internal, private)
        """
        assert ctx is not None
        client = ctx.request_context.lifespan_context.client

        try:
            visibility_enum = RepoVisibility(visibility)
            request = CreateRepositoryRequest(
                name=name,
                description=description or None,
                visibility=visibility_enum,
            )

            result = await client.repositories.create(request=request)

            return (
                f"Repository created successfully!\n\n"
                f"Name: {result.name}\n"
                f"Slug: {result.slug}\n"
                f"Visibility: {result.visibility}\n"
                f"Default Branch: {result.default_branch}\n"
                f"Web URL: {result.web_url}\n"
                f"Clone (SSH): {result.clone_url.ssh if result.clone_url else 'N/A'}"
            )
        except Exception as e:
            return f"Error creating repository: {e}"

    @mcp.tool()
    async def update_repository(
        owner: str,
        repo: str,
        description: str | None = None,
        default_branch: str | None = None,
        visibility: str | None = None,
        ctx: Context | None = None,
    ) -> str:
        """Update repository settings.

        Args:
            owner: Repository owner
            repo: Repository name
            description: New description (optional)
            default_branch: New default branch (optional)
            visibility: New visibility (optional)
        """
        assert ctx is not None
        client = ctx.request_context.lifespan_context.client

        try:
            request = UpdateRepositoryRequest()
            if description is not None:
                request.description = description
            if default_branch is not None:
                request.default_branch = default_branch
            if visibility is not None:
                request.visibility = RepoVisibility(visibility)

            result = await client.repositories.update(
                owner=owner,
                repo=repo,
                request=request,
            )

            return (
                f"Repository updated successfully!\n\n"
                f"Name: {result.name}\n"
                f"Description: {result.description or 'No description'}\n"
                f"Default Branch: {result.default_branch}\n"
                f"Visibility: {result.visibility}"
            )
        except Exception as e:
            return f"Error updating repository: {e}"

    @mcp.tool()
    async def delete_repository(
        owner: str,
        repo: str,
        ctx: Context | None = None,
    ) -> str:
        """Delete a repository.

        Args:
            owner: Repository owner
            repo: Repository name
        """
        assert ctx is not None
        client = ctx.request_context.lifespan_context.client

        try:
            await client.repositories.delete(owner=owner, repo=repo)
            return f"Repository '{owner}/{repo}' deleted successfully"
        except Exception as e:
            return f"Error deleting repository: {e}"

    @mcp.tool()
    async def list_branches(
        owner: str,
        repo: str,
        page: int = 1,
        per_page: int = 30,
        ctx: Context | None = None,
    ) -> str:
        """List branches in a repository.

        Args:
            owner: Repository owner
            repo: Repository name
            page: Page number
            per_page: Items per page
        """
        assert ctx is not None
        client = ctx.request_context.lifespan_context.client

        try:
            result = await client.repositories.list_branches(
                owner=owner,
                repo=repo,
                page=page,
                per_page=per_page,
            )

            branches = result.branches if hasattr(result, "branches") else []
            if not branches:
                return f"No branches found in '{owner}/{repo}'"

            lines = [f"Branches in '{owner}/{repo}':"]
            for branch in branches:
                commit_info = f" ({branch.commit.hash[:7]})" if branch.commit else ""
                lines.append(f"- {branch.name}{commit_info}")

            return "\n".join(lines)
        except Exception as e:
            return f"Error listing branches: {e}"

    @mcp.tool()
    async def list_tags(
        owner: str,
        repo: str,
        page: int = 1,
        per_page: int = 30,
        ctx: Context | None = None,
    ) -> str:
        """List tags in a repository.

        Args:
            owner: Repository owner
            repo: Repository name
            page: Page number
            per_page: Items per page
        """
        assert ctx is not None
        client = ctx.request_context.lifespan_context.client

        try:
            result = await client.repositories.list_tags(
                owner=owner,
                repo=repo,
                page=page,
                per_page=per_page,
            )

            tags = result.tags if hasattr(result, "tags") else []
            if not tags:
                return f"No tags found in '{owner}/{repo}'"

            lines = [f"Tags in '{owner}/{repo}':"]
            for tag in tags:
                commit_info = f" -> {tag.commit.hash[:7] if tag.commit else 'unknown'}"
                target = f" (target: {tag.target})" if hasattr(tag, "target") and tag.target else ""
                lines.append(f"- {tag.name}{commit_info}{target}")

            return "\n".join(lines)
        except Exception as e:
            return f"Error listing tags: {e}"

    @mcp.tool()
    async def get_file_tree(
        owner: str,
        repo: str,
        revision: str = "",
        path: str = "",
        recursive: bool = False,
        ctx: Context | None = None,
    ) -> str:
        """Get the file tree of a repository.

        Args:
            owner: Repository owner
            repo: Repository name
            revision: Git reference (branch, tag, or commit SHA). Uses default branch if empty.
            path: Path within repository. Root if empty.
            recursive: Whether to retrieve recursively
        """
        assert ctx is not None
        client = ctx.request_context.lifespan_context.client

        try:
            result = await client.repositories.get_file_tree(
                owner=owner,
                repo=repo,
                revision=revision or None,
                path=path or None,
                recursive=recursive,
            )

            trees = result.trees if hasattr(result, "trees") else []
            if not trees:
                return f"No files found at path '{path or '/'}'"

            lines = [f"Files in '{owner}/{repo}' at '{path or '/'}':"]
            for item in trees:
                icon = "📁" if item.type == "directory" else "📄"
                lines.append(f"{icon} {item.path}")

            return "\n".join(lines)
        except Exception as e:
            return f"Error getting file tree: {e}"
