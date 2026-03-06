# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install (editable, with dev dependencies)
pip install -e ".[dev]"

# Lint and format
ruff check cliject
ruff format cliject
ruff format --check cliject   # CI check only

# Run all tests
pytest

# Run a single test file or test
pytest tests/test_board.py
pytest tests/test_board.py::test_fetch_board_viewer
```

If using pixi environments, tasks mirror the above: `pixi run test`, `pixi run lint`, `pixi run fmt`.

## Architecture

The data flow is: `main.py` (CLI) → `board.py` (business logic) → `api.py` (HTTP) → GitHub GraphQL API.

**`auth.py`** — calls `gh auth token` via subprocess to get a Bearer token. `get_viewer_login()` fetches the authenticated user's login (used for `--me` filtering).

**`api.py`** — two functions: `execute_query` (single GraphQL call, raises `RuntimeError` on GraphQL errors) and `paginate_query` (follows cursor pagination given a dot-path to the connection object).

**`queries.py`** — four GraphQL query strings. `GET_PROJECT_FIELDS` and `GET_PROJECT_ITEMS` both use `@skip(if: $isOrg)` / `@include(if: $isOrg)` to branch between `viewer` and `organization` roots in a single query, controlled by the `$isOrg` boolean variable.

**`board.py`** — `fetch_projects` lists projects; `fetch_board` orchestrates two API calls (fields first, then paginated items), parses them into dataclasses, and groups items into `BoardColumn`s. Column order follows `status_options` from the field definition, not from items. `fieldValues.nodes` contains empty `{}` dicts for unmatched fragments — always guard with `if not fv: continue`.

**`models.py`** — pure dataclasses: `Project`, `Board`, `BoardColumn`, `BoardItem`, `StatusOption`, `Label`, `Assignee`. No logic.

**`render.py`** — Rich-based rendering. `render_board` outputs a kanban layout (columns side by side); `render_board_list` outputs a list view (items under status headings). Label colors use Rich hex syntax: `[bold on #rrggbb]text[/]`.

**`config.py`** — reads `~/.config/cliject/config.json` for `default_board`, `default_view`, and per-org defaults under `orgs.<name>.default_board`.

## Key Pitfalls

- `GET_PROJECT_FIELDS` / `GET_PROJECT_ITEMS` duplicate their body for viewer vs org — both sides must be kept in sync when modifying queries.
- `--group-by` works on any `ProjectV2SingleSelectField`, not just `Status`. The field match is case-insensitive.
- Items with no matching status value go into `Board.no_status_items`, rendered as a trailing column.
