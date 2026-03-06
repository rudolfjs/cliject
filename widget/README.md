# cliject macOS widget

A menu bar plugin for [xbar](https://xbarapp.com) or [SwiftBar](https://swiftbar.app) that shows a single GitHub Projects V2 board column in your menu bar. Each item is clickable and opens directly in GitHub.

![menu bar showing "In progress / Today (4)" with issues listed in dropdown]

## Prerequisites

- cliject installed (`pip install -e /path/to/cliject`)
- `gh` CLI authenticated with the `read:project` scope
- xbar or SwiftBar installed

## Setup

**1. Configure cliject** (`~/.config/cliject/config.json`):

```json
{
  "default_board": 4,
  "default_column": "In progress / Today"
}
```

**2. Install the plugin** by symlinking into your plugins directory:

```bash
# xbar
mkdir -p "$HOME/Library/Application Support/xbar/plugins"
ln -s "$(pwd)/cliject.1m.sh" "$HOME/Library/Application Support/xbar/plugins/"

# SwiftBar
mkdir -p "$HOME/Library/Application Support/SwiftBar/Plugins"
ln -s "$(pwd)/cliject.1m.sh" "$HOME/Library/Application Support/SwiftBar/Plugins/"
```

**3. Refresh** xbar/SwiftBar — the column name and item count will appear in your menu bar.

The plugin refreshes every minute (`1m` in the filename).

## Configuration

To override settings without touching `config.json`, edit the variables at the top of `cliject.1m.sh`:

| Variable | Description |
|---|---|
| `CLIJECT_BIN` | Full path to `cliject` binary (needed if it's not on `$PATH` in a non-login shell) |
| `CLIJECT_BOARD` | Project number, overrides `default_board` in config |
| `CLIJECT_COLUMN` | Column name, overrides `default_column` in config |
| `CLIJECT_ORG` | GitHub organization login (for org projects) |

## Troubleshooting

**"cliject not found"** — the menu bar plugin runs in a non-login shell so conda/pyenv environments are not activated. Set `CLIJECT_BIN` to the absolute path of your `cliject` binary:

```bash
which cliject   # run this in your normal terminal to find the path
```

Then uncomment and set in the script:
```bash
CLIJECT_BIN="/Users/you/miniconda3/bin/cliject"
```

**"cliject error"** — click the menu bar item to see the full error message in the dropdown.
