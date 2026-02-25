"""Tests for release tools."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from sourcecraft_mcp.tools import releases


class TestListReleases:
    """Test list_releases tool."""

    @pytest.mark.asyncio
    async def test_list_releases_success(self, mock_client, mock_context):
        """Test successful release listing."""
        mock_release1 = MagicMock()
        mock_release1.tag = "v1.0.0"
        mock_release1.title = "Version 1.0.0"
        mock_release1.status = "published"
        mock_release1.is_latest = True
        mock_release1.is_pre_release = False

        mock_release2 = MagicMock()
        mock_release2.tag = "v0.9.0"
        mock_release2.title = "Beta Release"
        mock_release2.status = "draft"
        mock_release2.is_latest = False
        mock_release2.is_pre_release = True

        mock_result = MagicMock()
        mock_result.releases = [mock_release1, mock_release2]
        mock_result.next_page_token = None

        mock_client.releases.list = AsyncMock(return_value=mock_result)

        result = await releases.list_releases(
            owner="test",
            repo="test-repo",
            ctx=mock_context,
        )

        assert "v1.0.0" in result
        assert "Version 1.0.0" in result
        assert "LATEST" in result
        assert "PRE-RELEASE" in result
        assert "published" in result
        assert "draft" in result

    @pytest.mark.asyncio
    async def test_list_releases_empty(self, mock_client, mock_context):
        """Test listing with no releases."""
        mock_result = MagicMock()
        mock_result.releases = []

        mock_client.releases.list = AsyncMock(return_value=mock_result)

        result = await releases.list_releases(
            owner="test",
            repo="test-repo",
            ctx=mock_context,
        )

        assert "No releases found" in result

    @pytest.mark.asyncio
    async def test_list_releases_with_pagination(self, mock_client, mock_context):
        """Test listing with pagination."""
        mock_release = MagicMock()
        mock_release.tag = "v1.0.0"
        mock_release.title = "Release"
        mock_release.status = "published"
        mock_release.is_latest = True
        mock_release.is_pre_release = False

        mock_result = MagicMock()
        mock_result.releases = [mock_release]
        mock_result.next_page_token = "next_page"

        mock_client.releases.list = AsyncMock(return_value=mock_result)

        result = await releases.list_releases(
            owner="test",
            repo="test-repo",
            page_size=10,
            page_token="token",
            ctx=mock_context,
        )

        assert "More results available" in result
        mock_client.releases.list.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_releases_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.releases.list = AsyncMock(side_effect=Exception("API Error"))

        result = await releases.list_releases(
            owner="test",
            repo="test-repo",
            ctx=mock_context,
        )

        assert "Error listing releases" in result


class TestGetRelease:
    """Test get_release tool."""

    @pytest.mark.asyncio
    async def test_get_release_success(self, mock_client, mock_context):
        """Test successful release retrieval."""
        mock_release = MagicMock()
        mock_release.tag = "v1.0.0"
        mock_release.title = "First Release"
        mock_release.status = "published"
        mock_release.is_latest = True
        mock_release.is_pre_release = False
        mock_release.author = MagicMock(slug="authoruser")
        mock_release.hash = "abc123def456"
        mock_release.release_notes = "This is the first release"

        asset1 = MagicMock()
        asset1.name = "app.tar.gz"
        asset2 = MagicMock()
        asset2.name = "checksums.txt"
        mock_release.assets = [asset1, asset2]

        mock_release.created_at = "2024-01-01"
        mock_release.released_at = "2024-01-02"

        mock_client.releases.get_by_tag = AsyncMock(return_value=mock_release)

        result = await releases.get_release(
            owner="test",
            repo="test-repo",
            tag="v1.0.0",
            ctx=mock_context,
        )

        assert "v1.0.0" in result
        assert "First Release" in result
        assert "authoruser" in result
        assert "abc123d" in result  # First 7 chars of hash
        assert "first release" in result
        assert "app.tar.gz" in result
        assert "Assets (2)" in result
        assert "2024-01-01" in result

    @pytest.mark.asyncio
    async def test_get_release_no_optional_fields(self, mock_client, mock_context):
        """Test release without optional fields."""
        mock_release = MagicMock()
        mock_release.tag = "v0.1.0"
        mock_release.title = None
        mock_release.status = "draft"
        mock_release.is_latest = False
        mock_release.is_pre_release = True
        mock_release.author = None
        mock_release.hash = None
        mock_release.release_notes = None
        mock_release.assets = []
        mock_release.created_at = "2024-01-01"
        mock_release.released_at = None

        mock_client.releases.get_by_tag = AsyncMock(return_value=mock_release)

        result = await releases.get_release(
            owner="test",
            repo="test-repo",
            tag="v0.1.0",
            ctx=mock_context,
        )

        assert "v0.1.0" in result
        assert "unknown" in result
        assert "Not yet released" in result

    @pytest.mark.asyncio
    async def test_get_release_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.releases.get_by_tag = AsyncMock(side_effect=Exception("API Error"))

        result = await releases.get_release(
            owner="test",
            repo="test-repo",
            tag="v1.0.0",
            ctx=mock_context,
        )

        assert "Error getting release" in result


class TestGetLatestRelease:
    """Test get_latest_release tool."""

    @pytest.mark.asyncio
    async def test_get_latest_release_success(self, mock_client, mock_context):
        """Test successful latest release retrieval."""
        mock_release = MagicMock()
        mock_release.tag = "v2.0.0"
        mock_release.title = "Latest Release"
        mock_release.status = "published"
        mock_release.is_pre_release = False
        mock_release.hash = "def789abc012"
        mock_release.release_notes = "Latest features"

        asset = MagicMock()
        asset.name = "release.zip"
        mock_release.assets = [asset]

        mock_client.releases.get_latest = AsyncMock(return_value=mock_release)

        result = await releases.get_latest_release(
            owner="test",
            repo="test-repo",
            ctx=mock_context,
        )

        assert "Latest Release" in result
        assert "v2.0.0" in result
        assert "Latest features" in result
        assert "release.zip" in result

    @pytest.mark.asyncio
    async def test_get_latest_release_pre_release(self, mock_client, mock_context):
        """Test latest pre-release."""
        mock_release = MagicMock()
        mock_release.tag = "v2.0.0-beta"
        mock_release.title = "Beta"
        mock_release.status = "published"
        mock_release.is_pre_release = True
        mock_release.hash = None
        mock_release.release_notes = None
        mock_release.assets = []

        mock_client.releases.get_latest = AsyncMock(return_value=mock_release)

        result = await releases.get_latest_release(
            owner="test",
            repo="test-repo",
            ctx=mock_context,
        )

        assert "PRE-RELEASE" in result
        assert "v2.0.0-beta" in result

    @pytest.mark.asyncio
    async def test_get_latest_release_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.releases.get_latest = AsyncMock(side_effect=Exception("API Error"))

        result = await releases.get_latest_release(
            owner="test",
            repo="test-repo",
            ctx=mock_context,
        )

        assert "Error getting latest release" in result


class TestCreateRelease:
    """Test create_release tool."""

    @pytest.mark.asyncio
    async def test_create_release_published(self, mock_client, mock_context):
        """Test creating a published release."""
        mock_release = MagicMock()
        mock_release.tag = "v1.0.0"
        mock_release.title = "Release 1.0.0"
        mock_release.status = "published"
        mock_release.author = MagicMock(slug="creator")

        mock_client.releases.create = AsyncMock(return_value=mock_release)

        result = await releases.create_release(
            owner="test",
            repo="test-repo",
            tag="v1.0.0",
            title="Release 1.0.0",
            release_notes="First release",
            target_branch="main",
            publish=True,
            ctx=mock_context,
        )

        assert "Release created as published" in result
        assert "v1.0.0" in result
        assert "creator" in result

    @pytest.mark.asyncio
    async def test_create_release_draft(self, mock_client, mock_context):
        """Test creating a draft release."""
        mock_release = MagicMock()
        mock_release.tag = "v1.0.0"
        mock_release.title = "Draft Release"
        mock_release.status = "draft"
        mock_release.author = MagicMock(slug="creator")

        mock_client.releases.create = AsyncMock(return_value=mock_release)

        result = await releases.create_release(
            owner="test",
            repo="test-repo",
            tag="v1.0.0",
            title="Draft Release",
            publish=False,
            ctx=mock_context,
        )

        assert "Release created as draft" in result

    @pytest.mark.asyncio
    async def test_create_release_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.releases.create = AsyncMock(side_effect=Exception("API Error"))

        result = await releases.create_release(
            owner="test",
            repo="test-repo",
            tag="v1.0.0",
            title="Release",
            ctx=mock_context,
        )

        assert "Error creating release" in result


class TestUpdateRelease:
    """Test update_release tool."""

    @pytest.mark.asyncio
    async def test_update_release_success(self, mock_client, mock_context):
        """Test successful release update."""
        mock_release = MagicMock()
        mock_release.tag = "v1.0.0"
        mock_release.title = "Updated Title"
        mock_release.status = "published"

        mock_client.releases.update_by_tag = AsyncMock(return_value=mock_release)

        result = await releases.update_release(
            owner="test",
            repo="test-repo",
            tag="v1.0.0",
            title="Updated Title",
            release_notes="Updated notes",
            ctx=mock_context,
        )

        assert "Release updated" in result
        assert "Updated Title" in result

    @pytest.mark.asyncio
    async def test_update_release_partial(self, mock_client, mock_context):
        """Test partial update (only title)."""
        mock_release = MagicMock()
        mock_release.tag = "v1.0.0"
        mock_release.title = "New Title"
        mock_release.status = "published"

        mock_client.releases.update_by_tag = AsyncMock(return_value=mock_release)

        result = await releases.update_release(
            owner="test",
            repo="test-repo",
            tag="v1.0.0",
            title="New Title",
            ctx=mock_context,
        )

        assert "New Title" in result

    @pytest.mark.asyncio
    async def test_update_release_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.releases.update_by_tag = AsyncMock(side_effect=Exception("API Error"))

        result = await releases.update_release(
            owner="test",
            repo="test-repo",
            tag="v1.0.0",
            title="New Title",
            ctx=mock_context,
        )

        assert "Error updating release" in result


class TestPublishRelease:
    """Test publish_release tool."""

    @pytest.mark.asyncio
    async def test_publish_release_success(self, mock_client, mock_context):
        """Test successful release publishing."""
        mock_release = MagicMock()
        mock_release.tag = "v1.0.0"
        mock_release.status = "published"

        mock_client.releases.publish_by_tag = AsyncMock(return_value=mock_release)

        result = await releases.publish_release(
            owner="test",
            repo="test-repo",
            tag="v1.0.0",
            ctx=mock_context,
        )

        assert "Release v1.0.0 published" in result
        assert "published" in result

    @pytest.mark.asyncio
    async def test_publish_release_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.releases.publish_by_tag = AsyncMock(side_effect=Exception("API Error"))

        result = await releases.publish_release(
            owner="test",
            repo="test-repo",
            tag="v1.0.0",
            ctx=mock_context,
        )

        assert "Error publishing release" in result


class TestDiscardRelease:
    """Test discard_release tool."""

    @pytest.mark.asyncio
    async def test_discard_release_success(self, mock_client, mock_context):
        """Test successful release discarding."""
        mock_release = MagicMock()
        mock_release.tag = "v1.0.0"
        mock_release.status = "discarded"

        mock_client.releases.discard_by_tag = AsyncMock(return_value=mock_release)

        result = await releases.discard_release(
            owner="test",
            repo="test-repo",
            tag="v1.0.0",
            ctx=mock_context,
        )

        assert "Release v1.0.0 discarded" in result
        assert "discarded" in result

    @pytest.mark.asyncio
    async def test_discard_release_error(self, mock_client, mock_context):
        """Test error handling."""
        mock_client.releases.discard_by_tag = AsyncMock(side_effect=Exception("API Error"))

        result = await releases.discard_release(
            owner="test",
            repo="test-repo",
            tag="v1.0.0",
            ctx=mock_context,
        )

        assert "Error discarding release" in result
