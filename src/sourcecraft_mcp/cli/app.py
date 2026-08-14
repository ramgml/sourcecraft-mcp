"""SourceCraft CLI entry point."""

from __future__ import annotations

import typer

from sourcecraft_mcp.cli import cicd, issues, orgs, prs, releases, repos, users
from sourcecraft_mcp.cli.common import DEFAULT_BASE_URL, CliContext

app = typer.Typer(
    name="sourcecraft",
    help="CLI для работы с платформой SourceCraft: репозитории, issues, PR, CI/CD, релизы.",
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
)


@app.callback()
def main_callback(
    ctx: typer.Context,
    token: str | None = typer.Option(
        None,
        "--token",
        envvar="SOURCECRAFT_API_TOKEN",
        help="API токен SourceCraft (env: SOURCECRAFT_API_TOKEN).",
    ),
    base_url: str = typer.Option(
        DEFAULT_BASE_URL,
        "--base-url",
        envvar="SOURCECRAFT_BASE_URL",
        help="Базовый URL API (env: SOURCECRAFT_BASE_URL).",
    ),
    as_json: bool = typer.Option(
        False,
        "--json",
        help="Вывод в формате JSON (удобно для jq и скриптов).",
    ),
) -> None:
    """Global options for the SourceCraft CLI."""
    ctx.obj = CliContext(token=token, base_url=base_url, as_json=as_json)


app.add_typer(repos.app, name="repo", help="Работа с репозиториями.")
app.add_typer(issues.app, name="issue", help="Работа с issues.")
app.add_typer(prs.app, name="pr", help="Работа с pull requests.")
app.add_typer(cicd.app, name="ci", help="CI/CD: запуски, workflows, логи, артефакты.")
app.add_typer(releases.app, name="release", help="Работа с релизами.")
app.add_typer(users.app, name="user", help="Информация о пользователях.")
app.add_typer(orgs.app, name="org", help="Работа с организациями.")


def main() -> None:
    """CLI entry point."""
    app()


if __name__ == "__main__":
    main()
