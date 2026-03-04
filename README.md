# cliject - GitHub Project boards in the terminal

GitHub Projects V2 terminal board viewer. Fetches project data via the GitHub GraphQL API and renders it as a Kanban-style board in your terminal.

## Requirements

- Python 3.10+
- [gh CLI](https://cli.github.com/) authenticated (`gh auth login`)

## Installation

```bash
pip install -e .
```

## Usage

### List projects

```bash
# Personal projects
cliject list

# Organization projects
cliject list --org <orgname>

# Include closed projects
cliject list --closed
```

### View a project board

```bash
# By project number
cliject board 4

# Use the configured default board (no number needed)
cliject board

# Org project
cliject board 4 --org <orgname>

# Use the configured default board for an org
cliject board --org <orgname>

# Group by a different single-select field
cliject board 4 --group-by "Priority"

# Only show items assigned to you
cliject board 4 --me

# Show empty columns
cliject board 4 --show-empty

# List view (items as bullet list under status headings)
cliject board 4 --view list

# Kanban view (default)
cliject board 4 --view kanban
```

### All flags

| Command | Flag | Description |
|---------|------|-------------|
| `list` | `--org, -o` | GitHub organization login |
| `list` | `--closed` | Include closed projects |
| `board` | *(number)* | Project number — optional if a default is configured |
| `board` | `--org, -o` | GitHub organization login |
| `board` | `--group-by, -g` | Field name to group columns by (default: `Status`) |
| `board` | `--me` | Only show items assigned to you |
| `board` | `--show-empty` | Show columns that have no items |
| `board` | `--view, -v` | Display style: `kanban` (default) or `list` |

## Configuration

Create `~/.config/cliject/config.json` to set default board numbers:

```json
{
  "default_board": 4,
  "default_view": "list",
  "orgs": {
    "my-org": {
      "default_board": 7
    },
    "another-org": {
      "default_board": 2
    }
  }
}
```

- `default_board` — used by `cliject board` with no number and no `--org`
- `default_view` — preferred display style: `"kanban"` (default) or `"list"`; overridden by `--view`
- `orgs.<name>.default_board` — used by `cliject board --org <name>` with no number

## Project structure

```
cliject/
├── auth.py      # gh CLI token retrieval
├── api.py       # GraphQL client and paginator
├── config.py    # Config file loader (~/.config/cliject/config.json)
├── queries.py   # GraphQL query strings
├── models.py    # Dataclasses (Project, Board, BoardItem, …)
├── board.py     # Business logic: fetch_projects, fetch_board
├── render.py    # Rich terminal rendering
└── main.py      # Typer CLI entry point
```
