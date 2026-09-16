"""Tests for the SourceCraft CLI."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from typer.testing import CliRunner

from sourcecraft_mcp.cli import common
from sourcecraft_mcp.cli.app import app

runner = CliRunner()


def make_client() -> MagicMock:
    """Build a mocked SourceCraftClient with async resource clients."""
    client = MagicMock()
    client.close = AsyncMock()
    for domain in (
        "repositories",
        "issues",
        "pull_requests",
        "releases",
        "users",
        "organizations",
        "cicd",
    ):
        setattr(client, domain, MagicMock())
    return client


@pytest.fixture
def mock_client(monkeypatch):
    """Patch create_client to return a mocked client."""
    client = make_client()
    monkeypatch.setattr(common, "create_client", lambda ctx: client)
    return client


class TestGlobalOptions:
    """Global CLI behaviour."""

    def test_help(self):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "repo" in result.output
        assert "issue" in result.output
        assert "pr" in result.output
        assert "ci" in result.output
        assert "release" in result.output

    def test_missing_token_exits_2(self, monkeypatch):
        monkeypatch.delenv("SOURCECRAFT_API_TOKEN", raising=False)
        result = runner.invoke(app, ["user", "me"])
        assert result.exit_code == 2
        assert "API token is required" in result.output

    def test_invalid_repo_format(self, mock_client):
        result = runner.invoke(app, ["repo", "get", "no-slash"])
        assert result.exit_code == 2
        assert "owner/repo" in result.output

    def test_api_error_exits_1(self, mock_client):
        mock_client.users.get_current = AsyncMock(side_effect=RuntimeError("boom"))
        result = runner.invoke(app, ["user", "me"])
        assert result.exit_code == 1
        assert "boom" in result.output


class TestRepoCommands:
    """repo commands."""

    def test_list_table(self, mock_client):
        repo = MagicMock(slug="org/repo1", name="repo1", visibility="public", description="desc")
        result_model = MagicMock(repositories=[repo])
        mock_client.repositories.list = AsyncMock(return_value=result_model)

        result = runner.invoke(app, ["repo", "list"])
        assert result.exit_code == 0
        assert "org/repo1" in result.output
        mock_client.repositories.list.assert_awaited_once_with(username=None, page=1, per_page=30)

    def test_list_org(self, mock_client):
        result_model = MagicMock(repositories=[])
        mock_client.repositories.list_org_repos = AsyncMock(return_value=result_model)

        result = runner.invoke(app, ["repo", "list", "--org", "myorg"])
        assert result.exit_code == 0
        mock_client.repositories.list_org_repos.assert_awaited_once_with(
            org="myorg", page=1, per_page=30
        )

    def test_list_json(self, mock_client):
        mock_client.repositories.list = AsyncMock(
            return_value={"repositories": [{"slug": "org/repo1"}]}
        )
        result = runner.invoke(app, ["--json", "repo", "list"])
        assert result.exit_code == 0
        assert '"slug": "org/repo1"' in result.output

    def test_get(self, mock_client):
        repo_model = MagicMock(
            slug="org/repo",
            name="repo",
            visibility="private",
            description=None,
            default_branch="main",
            language=None,
            web_url="https://sourcecraft.dev/org/repo",
            clone_url=None,
            last_updated="2024-01-01",
        )
        mock_client.repositories.get = AsyncMock(return_value=repo_model)

        result = runner.invoke(app, ["repo", "get", "org/repo"])
        assert result.exit_code == 0
        mock_client.repositories.get.assert_awaited_once_with(owner="org", repo="repo")

    def test_delete_requires_confirmation(self, mock_client):
        mock_client.repositories.delete = AsyncMock()
        result = runner.invoke(app, ["repo", "delete", "org/repo"], input="n\n")
        assert result.exit_code != 0
        mock_client.repositories.delete.assert_not_called()

    def test_delete_with_yes(self, mock_client):
        mock_client.repositories.delete = AsyncMock()
        result = runner.invoke(app, ["repo", "delete", "org/repo", "--yes"])
        assert result.exit_code == 0
        mock_client.repositories.delete.assert_awaited_once_with(owner="org", repo="repo")

    def test_tree(self, mock_client):
        item = MagicMock(type="directory", path="src")
        mock_client.repositories.get_file_tree = AsyncMock(return_value=MagicMock(trees=[item]))

        result = runner.invoke(app, ["repo", "tree", "org/repo", "--recursive"])
        assert result.exit_code == 0
        mock_client.repositories.get_file_tree.assert_awaited_once_with(
            owner="org", repo="repo", revision=None, path=None, recursive=True
        )


class TestIssueCommands:
    """issue commands."""

    def test_list_with_filters(self, mock_client):
        issue = MagicMock(
            slug=1,
            title="Bug",
            status=MagicMock(name="Open"),
            priority="critical",
            assignee=MagicMock(slug="dev1"),
        )
        mock_client.issues.list = AsyncMock(return_value=MagicMock(data=[issue]))

        result = runner.invoke(
            app, ["issue", "list", "org/repo", "--status", "open", "--assignee", "dev1"]
        )
        assert result.exit_code == 0
        assert "Bug" in result.output
        kwargs = mock_client.issues.list.await_args.kwargs
        assert kwargs["owner"] == "org"
        assert kwargs["filters"].state == "open"
        assert kwargs["filters"].assignee_id == "dev1"

    def test_create(self, mock_client):
        created = MagicMock(
            slug=5, title="New", status=MagicMock(name="Open"), author=MagicMock(slug="me")
        )
        mock_client.issues.create = AsyncMock(return_value=created)

        result = runner.invoke(
            app, ["issue", "create", "org/repo", "--title", "New", "--body", "text"]
        )
        assert result.exit_code == 0
        kwargs = mock_client.issues.create.await_args.kwargs
        assert kwargs["request"].title == "New"
        assert kwargs["request"].body == "text"

    def test_close(self, mock_client):
        mock_client.issues.close = AsyncMock()
        result = runner.invoke(app, ["issue", "close", "org/repo", "7"])
        assert result.exit_code == 0
        mock_client.issues.close.assert_awaited_once_with(owner="org", repo="repo", issue_number=7)

    def test_comment(self, mock_client):
        mock_client.issues.create_comment = AsyncMock(
            return_value=MagicMock(author=MagicMock(slug="me"))
        )
        result = runner.invoke(app, ["issue", "comment", "org/repo", "7", "--body", "hi"])
        assert result.exit_code == 0
        mock_client.issues.create_comment.assert_awaited_once_with(
            owner="org", repo="repo", issue_number=7, body="hi"
        )


class TestPRCommands:
    """pr commands."""

    def test_list(self, mock_client):
        pr = MagicMock(
            slug=3,
            title="Fix",
            status="open",
            source_branch="feature",
            target_branch="main",
            author=MagicMock(slug="me"),
        )
        mock_client.pull_requests.list = AsyncMock(return_value=MagicMock(data=[pr]))

        result = runner.invoke(app, ["pr", "list", "org/repo", "--status", "open"])
        assert result.exit_code == 0
        assert "Fix" in result.output
        kwargs = mock_client.pull_requests.list.await_args.kwargs
        assert kwargs["filters"].state == "open"

    def test_create_publish(self, mock_client):
        pr = MagicMock(
            slug=3,
            title="Fix",
            source_branch="feature",
            target_branch="main",
            author=MagicMock(slug="me"),
        )
        mock_client.pull_requests.create = AsyncMock(return_value=pr)

        result = runner.invoke(
            app,
            [
                "pr",
                "create",
                "org/repo",
                "--title",
                "Fix",
                "--source",
                "feature",
                "--target",
                "main",
                "--publish",
            ],
        )
        assert result.exit_code == 0
        request = mock_client.pull_requests.create.await_args.kwargs["request"]
        assert request.publish is True
        assert request.source_branch == "feature"

    def test_merge_squash(self, mock_client):
        merged = MagicMock(merge_info=MagicMock(merge_commit_hash="abcdef1234"))
        mock_client.pull_requests.merge = AsyncMock(return_value=merged)

        result = runner.invoke(app, ["pr", "merge", "org/repo", "3", "--squash"])
        assert result.exit_code == 0
        assert "abcdef1" in result.output
        request = mock_client.pull_requests.merge.await_args.kwargs["request"]
        assert request.method == "squash"

    def test_review(self, mock_client):
        mock_client.pull_requests.set_review_decision = AsyncMock()
        result = runner.invoke(app, ["pr", "review", "org/repo", "3", "--decision", "approve"])
        assert result.exit_code == 0
        mock_client.pull_requests.set_review_decision.assert_awaited_once_with(
            owner="org", repo="repo", pull_number=3, decision="approve"
        )


class TestCICommands:
    """ci commands."""

    def test_runs(self, mock_client):
        run = MagicMock(
            slug="abc1",
            status="success",
            event_type="push",
            dates=MagicMock(created_at="2024-01-01"),
        )
        mock_client.cicd.list_runs = AsyncMock(
            return_value=MagicMock(runs=[run], next_page_token=None)
        )

        result = runner.invoke(app, ["ci", "runs", "org/repo"])
        assert result.exit_code == 0
        assert "abc1" in result.output

    def test_logs(self, mock_client):
        mock_client.cicd.get_cube_logs = AsyncMock(
            return_value=MagicMock(logs="line1\nline2", done=True, page_complete=True)
        )
        result = runner.invoke(app, ["ci", "logs", "org/repo", "r", "w", "t", "c"])
        assert result.exit_code == 0
        assert "line1" in result.output

    def test_trigger(self, mock_client):
        mock_client.cicd.create_pipeline = AsyncMock(
            return_value=MagicMock(id="p1", status="created")
        )
        result = runner.invoke(app, ["ci", "trigger", "org/repo", "build", "--branch", "dev"])
        assert result.exit_code == 0
        kwargs = mock_client.cicd.create_pipeline.await_args.kwargs
        assert kwargs["ref"] == "dev"
        assert kwargs["variables"] == {"workflows": ["build"]}


class TestReleaseCommands:
    """release commands."""

    def test_list(self, mock_client):
        release = MagicMock(
            tag="v1.0.0",
            title="First",
            status="published",
            is_latest=True,
            is_pre_release=False,
        )
        mock_client.releases.list = AsyncMock(
            return_value=MagicMock(data=[release], next_page_token=None)
        )

        result = runner.invoke(app, ["release", "list", "org/repo"])
        assert result.exit_code == 0
        assert "v1.0.0" in result.output

    def test_create_draft(self, mock_client):
        release = MagicMock(
            tag="v1.0.0", title="First", status="draft", author=MagicMock(slug="me")
        )
        mock_client.releases.create = AsyncMock(return_value=release)

        result = runner.invoke(app, ["release", "create", "org/repo", "v1.0.0", "--title", "First"])
        assert result.exit_code == 0
        request = mock_client.releases.create.await_args.kwargs["request"]
        assert request.tag_name == "v1.0.0"
        assert request.draft is True

    def test_publish(self, mock_client):
        mock_client.releases.publish_by_tag = AsyncMock(
            return_value=MagicMock(tag="v1.0.0", status="published")
        )
        result = runner.invoke(app, ["release", "publish", "org/repo", "v1.0.0"])
        assert result.exit_code == 0
        mock_client.releases.publish_by_tag.assert_awaited_once_with(
            owner="org", repo="repo", tag="v1.0.0"
        )


class TestUserAndOrgCommands:
    """user and org commands."""

    def test_user_me(self, mock_client):
        user = MagicMock(
            username="me",
            display_name="Me",
            bio=None,
            location=None,
            workplace=None,
            visibility="public",
        )
        mock_client.users.get_current = AsyncMock(return_value=user)

        result = runner.invoke(app, ["user", "me"])
        assert result.exit_code == 0
        assert "@me" in result.output

    def test_org_members(self, mock_client):
        member = MagicMock(user=MagicMock(slug="dev1"), role="admin")
        mock_client.organizations.list_members = AsyncMock(return_value=MagicMock(members=[member]))

        result = runner.invoke(app, ["org", "members", "myorg"])
        assert result.exit_code == 0
        assert "@dev1" in result.output
