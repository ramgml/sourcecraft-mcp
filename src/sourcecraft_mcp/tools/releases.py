"""Release tools for SourceCraft MCP server."""

from __future__ import annotations

from mcp.server.fastmcp import Context


def register_tools(mcp):
    """Register release tools with the MCP server."""

    @mcp.tool()
    async def list_releases(
        owner: str,
        repo: str,
        page_size: int = 30,
        page_token: str = "",
        ctx: Context | None = None,
    ) -> str:
        """List releases in a repository.

        Args:
            owner: Repository owner
            repo: Repository name
            page_size: Maximum number of releases to return
            page_token: Token for pagination
        """
        assert ctx is not None
        client = ctx.request_context.lifespan_context.client

        try:
            result = await client.releases.list(
                owner=owner,
                repo=repo,
                page_size=page_size,
                page_token=page_token or None,
            )

            releases = result.releases if hasattr(result, "releases") else []
            if not releases:
                return f"No releases found in '{owner}/{repo}'"

            lines = [f"Releases in '{owner}/{repo}':"]
            for release in releases:
                status_icon = "✅" if release.status == "published" else "📝"
                latest_marker = " (LATEST)" if release.is_latest else ""
                pre_release = " [PRE-RELEASE]" if release.is_pre_release else ""

                lines.append(
                    f"{status_icon} {release.tag}{latest_marker}{pre_release}\n"
                    f"   Title: {release.title or 'No title'}\n"
                    f"   Status: {release.status}"
                )

            if hasattr(result, "next_page_token") and result.next_page_token:
                lines.append("\n(More results available)")

            return "\n\n".join(lines)
        except Exception as e:
            return f"Error listing releases: {e}"

    @mcp.tool()
    async def get_release(
        owner: str,
        repo: str,
        tag: str,
        ctx: Context | None = None,
    ) -> str:
        """Get a release by tag.

        Args:
            owner: Repository owner
            repo: Repository name
            tag: Release tag
        """
        assert ctx is not None
        client = ctx.request_context.lifespan_context.client

        try:
            result = await client.releases.get_by_tag(
                owner=owner,
                repo=repo,
                tag=tag,
            )

            status_icon = "✅" if result.status == "published" else "📝"
            latest_marker = " (LATEST)" if result.is_latest else ""
            pre_release = " [PRE-RELEASE]" if result.is_pre_release else ""

            lines = [
                f"{status_icon} Release {result.tag}{latest_marker}{pre_release}",
                f"Title: {result.title or 'No title'}",
                f"Status: {result.status}",
                f"Author: @{result.author.slug if result.author else 'unknown'}",
            ]

            if result.hash:
                lines.append(f"Commit: {result.hash[:7]}")

            if result.release_notes:
                lines.extend(
                    [
                        "",
                        "Release Notes:",
                        result.release_notes,
                    ]
                )

            if result.assets:
                lines.extend(
                    [
                        "",
                        f"Assets ({len(result.assets)}):",
                    ]
                )
                for asset in result.assets:
                    lines.append(f"  • {asset.name}")

            lines.extend(
                [
                    "",
                    f"Created: {result.created_at}",
                    f"Released: {result.released_at or 'Not yet released'}",
                ]
            )

            return "\n".join(lines)
        except Exception as e:
            return f"Error getting release: {e}"

    @mcp.tool()
    async def get_latest_release(
        owner: str,
        repo: str,
        ctx: Context | None = None,
    ) -> str:
        """Get the latest release in a repository.

        Args:
            owner: Repository owner
            repo: Repository name
        """
        assert ctx is not None
        client = ctx.request_context.lifespan_context.client

        try:
            result = await client.releases.get_latest(
                owner=owner,
                repo=repo,
            )

            pre_release = " [PRE-RELEASE]" if result.is_pre_release else ""

            lines = [
                f"🌟 Latest Release: {result.tag}{pre_release}",
                f"Title: {result.title or 'No title'}",
                f"Status: {result.status}",
            ]

            if result.hash:
                lines.append(f"Commit: {result.hash[:7]}")

            if result.release_notes:
                lines.extend(
                    [
                        "",
                        "Release Notes:",
                        result.release_notes,
                    ]
                )

            if result.assets:
                lines.extend(
                    [
                        "",
                        f"Assets ({len(result.assets)}):",
                    ]
                )
                for asset in result.assets:
                    lines.append(f"  • {asset.name}")

            return "\n".join(lines)
        except Exception as e:
            return f"Error getting latest release: {e}"

    @mcp.tool()
    async def create_release(
        owner: str,
        repo: str,
        tag: str,
        title: str,
        release_notes: str = "",
        target_branch: str = "",
        publish: bool = False,
        ctx: Context | None = None,
    ) -> str:
        """Create a new release.

        Args:
            owner: Repository owner
            repo: Repository name
            tag: Release tag (e.g., "v1.0.0")
            title: Release title
            release_notes: Release notes/description
            target_branch: Branch to create tag on (if tag doesn't exist)
            publish: Whether to publish immediately (False = draft)
        """
        assert ctx is not None
        client = ctx.request_context.lifespan_context.client

        try:
            from pysourcecraft.models import CreateReleaseRequest

            request = CreateReleaseRequest(
                tag=tag,
                title=title,
                release_notes=release_notes or None,
                target_branch=target_branch or None,
                publish=publish,
            )

            result = await client.releases.create(
                owner=owner,
                repo=repo,
                request=request,
            )

            status = "published" if publish else "draft"
            return (
                f"Release created as {status}!\n\n"
                f"Tag: {result.tag}\n"
                f"Title: {result.title}\n"
                f"Status: {result.status}\n"
                f"Author: @{result.author.slug if result.author else 'unknown'}"
            )
        except Exception as e:
            return f"Error creating release: {e}"

    @mcp.tool()
    async def update_release(
        owner: str,
        repo: str,
        tag: str,
        title: str | None = None,
        release_notes: str | None = None,
        ctx: Context | None = None,
    ) -> str:
        """Update a release.

        Args:
            owner: Repository owner
            repo: Repository name
            tag: Release tag
            title: New title (optional)
            release_notes: New release notes (optional)
        """
        assert ctx is not None
        client = ctx.request_context.lifespan_context.client

        try:
            from pysourcecraft.models import UpdateReleaseRequest

            request = UpdateReleaseRequest()
            if title is not None:
                request.title = title
            if release_notes is not None:
                request.release_notes = release_notes

            result = await client.releases.update_by_tag(
                owner=owner,
                repo=repo,
                tag=tag,
                request=request,
            )

            return (
                f"Release updated!\n\n"
                f"Tag: {result.tag}\n"
                f"Title: {result.title}\n"
                f"Status: {result.status}"
            )
        except Exception as e:
            return f"Error updating release: {e}"

    @mcp.tool()
    async def publish_release(
        owner: str,
        repo: str,
        tag: str,
        ctx: Context | None = None,
    ) -> str:
        """Publish a draft release.

        Args:
            owner: Repository owner
            repo: Repository name
            tag: Release tag
        """
        assert ctx is not None
        client = ctx.request_context.lifespan_context.client

        try:
            result = await client.releases.publish_by_tag(
                owner=owner,
                repo=repo,
                tag=tag,
            )
            return f"Release {result.tag} published! Status: {result.status}"
        except Exception as e:
            return f"Error publishing release: {e}"

    @mcp.tool()
    async def discard_release(
        owner: str,
        repo: str,
        tag: str,
        ctx: Context | None = None,
    ) -> str:
        """Discard a published release.

        Args:
            owner: Repository owner
            repo: Repository name
            tag: Release tag
        """
        assert ctx is not None
        client = ctx.request_context.lifespan_context.client

        try:
            result = await client.releases.discard_by_tag(
                owner=owner,
                repo=repo,
                tag=tag,
            )
            return f"Release {result.tag} discarded. Status: {result.status}"
        except Exception as e:
            return f"Error discarding release: {e}"
