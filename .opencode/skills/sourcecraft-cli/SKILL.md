---
name: sourcecraft-cli
description: Work with the SourceCraft platform (sourcecraft.dev) from the terminal using the `sourcecraft` CLI — repositories, issues, pull requests, CI/CD runs and logs, releases, users, organizations. Use when asked to list/create/update repos, triage issues, review or merge PRs, inspect CI failures, cut releases, or query SourceCraft orgs/users via CLI. For writing .sourcecraft/ci.yaml pipeline configs use the sourcecraft-ci skill instead.
---

# SourceCraft CLI (`sourcecraft`)

Terminal client for **SourceCraft** (git platform, sourcecraft.dev). Ships with the `sourcecraft-mcp` package (repo: `ssh://ssh.sourcecraft.dev/ram56/sourcecraft-mcp.git`), built on Typer + Rich over the async `pysourcecraft` API client.

If `sourcecraft` is not on PATH, run it from the project: `uv run sourcecraft ...` in the sourcecraft-mcp checkout, or `uvx --from "git+https://git.sourcecraft.dev/ram56/sourcecraft-mcp.git" sourcecraft ...`.

## Authentication

```bash
export SOURCECRAFT_API_TOKEN="..."                        # required
export SOURCECRAFT_BASE_URL="https://api.sourcecraft.tech" # optional, this is the default
```

- Token: SourceCraft UI → Settings → Access → Personal Access Tokens.
- `--token` flag overrides the env var.
- Missing token → exit code 2 with an error on stderr. Never ask the user to paste the token into chat; check env first.

## Command model

```
sourcecraft [--token T] [--base-url U] [--json] GROUP COMMAND [ARGS]
```

Groups: `repo`, `issue`, `pr`, `ci`, `release`, `user`, `org`. Every group and command has `--help` — consult it instead of guessing flags.

- **Global `--json` goes BEFORE the group**: `sourcecraft --json repo list`, not `repo list --json`. Use `--json | jq` for scripting and for exact field extraction.
- **Repositories are addressed as one `owner/repo` argument** (positional, e.g. `myorg/backend-api`).
- Default output is Rich tables; errors go to stderr, exit code 1 = API/runtime error, 2 = usage/config error.
- Pagination: `--page`/`--per-page` for repos/issues/PRs; `--page-size`/`--page-token` for CI runs, releases, user issues/PRs (token-based; the table output prints the next token).

## Command map

| Domain | Commands |
|---|---|
| `repo` | `list [--org ORG \| --user NAME]`, `get`, `create NAME [-d desc] [-v public\|internal\|private]`, `update`, `delete [-y]`, `branches`, `tags`, `tree [-r REV] [-p PATH] [-R]` |
| `issue` | `list [-s STATUS] [-a ASSIGNEE_ID] [-l LABEL]`, `get N`, `create -t TITLE [-b BODY]`, `update N`, `close N`, `reopen N`, `comments N`, `comment N -b BODY` |
| `pr` | `list [-s draft\|open\|merging\|merged\|discarded]`, `get N`, `create -t TITLE --source B --target B [--publish]`, `update N`, `merge N [--squash]`, `publish N`, `discard N`, `reviewers N`, `add-reviewer N -u USER_ID`, `review N -d approve\|trust\|block\|abstain` |
| `ci` | `runs`, `run RUN`, `workflow RUN WORKFLOW`, `logs RUN WORKFLOW TASK CUBE [--page N]`, `artifacts RUN WORKFLOW TASK CUBE`, `trigger WORKFLOW... [--branch B]` |
| `release` | `list`, `get TAG`, `latest`, `create TAG -t TITLE [-n NOTES] [--publish]`, `update TAG`, `publish TAG`, `discard TAG` |
| `user` | `me`, `get USERNAME`, `issues`, `prs USERNAME [--role author\|reviewer\|any]` |
| `org` | `list`, `get ORG`, `repos ORG`, `members ORG` |

## Typical agent workflows

**Triage issues:**
```bash
sourcecraft issue list ORG/REPO --status open
sourcecraft --json issue list ORG/REPO --status open | jq '.data[] | {slug, title, priority}'
sourcecraft issue comment ORG/REPO 42 --body "..."
sourcecraft issue close ORG/REPO 42
```

**Review and merge a PR:**
```bash
sourcecraft pr list ORG/REPO --status open
sourcecraft pr get ORG/REPO 45
sourcecraft pr review ORG/REPO 45 --decision approve
sourcecraft pr merge ORG/REPO 45 --squash
```

**Debug a failing CI run** (drill-down: run → workflow → task → cube logs):
```bash
sourcecraft ci runs ORG/REPO                          # find run slug + status
sourcecraft ci run ORG/REPO RUN_SLUG                  # workflows inside the run
sourcecraft ci workflow ORG/REPO RUN_SLUG WORKFLOW    # tasks inside the workflow
sourcecraft ci logs ORG/REPO RUN_SLUG WORKFLOW TASK CUBE          # cube logs
sourcecraft ci artifacts ORG/REPO RUN_SLUG WORKFLOW TASK CUBE     # artifact URLs
```
Task/cube slugs come from the run's `ci.yaml` (`workflows → tasks → cubes`). For authoring or fixing that config, use the **sourcecraft-ci** skill.

**Cut a release:**
```bash
sourcecraft release create ORG/REPO v1.2.0 --title "v1.2.0" --notes "..." --publish
sourcecraft release latest ORG/REPO
```

## Gotchas

1. **PRs and releases are created as drafts by default** — pass `--publish` to make them visible immediately. Draft PRs can be published later with `pr publish N`.
2. **Assignee/reviewer flags take user IDs, not usernames.** Look users up via `sourcecraft user get USERNAME` / `org members ORG` first.
3. **`repo delete` asks for confirmation**; use `-y` in non-interactive runs, but confirm with the user before deleting anything.
4. **CI logs are paginated** — if output ends with "Ещё логи", request the next `--page`.
5. **Status enums**: issues use slugs like `open`/`inProgress`/`paused`/`closed`; priorities are `trivial|minor|normal|critical|blocker`; PR review decisions are `approve|trust|block|abstain`.
6. **Filtering `issue list --assignee` and `pr list --author` expects IDs**; `--status` on `pr list` takes the enum value (`open`, `merged`, ...).
7. The CLI is read/write — prefer read-only commands unless the user explicitly asked to create/modify/merge/delete.

## Related

- **sourcecraft-ci** skill — authoring `.sourcecraft/ci.yaml` pipeline configs.
- **sourcecraft-mcp** — the same operations exposed as MCP tools (`list_issues`, `merge_pull_request`, ...) when an MCP server is configured instead of the CLI.
- API docs: https://sourcecraft.dev/portal/docs/ (append `.md` to any docs URL for raw markdown).
