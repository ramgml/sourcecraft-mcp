"""Organization commands."""

from __future__ import annotations

import typer

from sourcecraft_mcp.cli.common import render_fields, render_table, run_command

app = typer.Typer(no_args_is_help=True)

OrgArg = typer.Argument(..., help="Slug организации.")


@app.command("list")
def list_orgs(
    ctx: typer.Context,
    page: int = typer.Option(1, "--page"),
    per_page: int = typer.Option(30, "--per-page"),
) -> None:
    """Список организаций."""

    async def handler(client):
        return await client.organizations.list(page=page, per_page=per_page)

    def render(result):
        orgs = getattr(result, "organizations", None) or []
        render_table(
            "Organizations",
            ["Slug", "Name"],
            [[o.slug, o.name] for o in orgs],
        )

    run_command(ctx, handler, render)


@app.command("get")
def get_org(ctx: typer.Context, org: str = OrgArg) -> None:
    """Информация об организации."""

    async def handler(client):
        return await client.organizations.get(org=org)

    def render(o):
        render_fields(
            f"Organization {o.slug}",
            [
                ("Name", o.name),
                ("Description", getattr(o, "description", None)),
                ("Website", getattr(o, "website", None)),
                ("Created", getattr(o, "created_at", None)),
            ],
        )

    run_command(ctx, handler, render)


@app.command("repos")
def org_repos(
    ctx: typer.Context,
    org: str = OrgArg,
    page: int = typer.Option(1, "--page"),
    per_page: int = typer.Option(30, "--per-page"),
) -> None:
    """Репозитории организации."""

    async def handler(client):
        return await client.organizations.list_repos(org=org, page=page, per_page=per_page)

    def render(result):
        repos = getattr(result, "repositories", None) or []
        render_table(
            f"Repositories in {org}",
            ["Slug", "Visibility", "Description"],
            [[r.slug, r.visibility, r.description] for r in repos],
        )

    run_command(ctx, handler, render)


@app.command("members")
def org_members(
    ctx: typer.Context,
    org: str = OrgArg,
    page: int = typer.Option(1, "--page"),
    per_page: int = typer.Option(30, "--per-page"),
) -> None:
    """Участники организации."""

    async def handler(client):
        return await client.organizations.list_members(org=org, page=page, per_page=per_page)

    def render(result):
        members = getattr(result, "members", None) or []
        render_table(
            f"Members of {org}",
            ["User", "Role"],
            [
                [
                    f"@{m.user.slug}" if hasattr(m, "user") and m.user else getattr(m, "slug", ""),
                    getattr(m, "role", ""),
                ]
                for m in members
            ],
        )

    run_command(ctx, handler, render)
