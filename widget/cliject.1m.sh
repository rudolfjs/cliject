#!/bin/bash
# <xbar.title>Cliject Board Column</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>cliject</xbar.author>
# <xbar.desc>Shows a GitHub Projects V2 board column in the menu bar</xbar.desc>
# <xbar.dependencies>python,cliject,gh</xbar.dependencies>
#
# Setup:
#   1. Install cliject: pip install -e /path/to/cliject
#   2. Set default_board and default_column in ~/.config/cliject/config.json
#   3. Symlink or copy this script into your xbar/SwiftBar plugins directory
#
# Optional overrides (uncomment and set as needed):
# CLIJECT_BIN="/Users/you/miniconda3/bin/cliject"  # full path if cliject isn't on PATH
# CLIJECT_BOARD=4
# CLIJECT_COLUMN="In progress / Today"
# CLIJECT_ORG=""

export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:$HOME/miniconda3/bin:$HOME/miniconda3/envs/base/bin:$HOME/anaconda3/bin:$HOME/miniforge3/bin:$PATH"

# Resolve binary: use CLIJECT_BIN override, or search PATH
CLIJECT="${CLIJECT_BIN:-$(command -v cliject)}"
if [ -z "$CLIJECT" ]; then
    echo "cliject not found | color=red"
    echo "---"
    echo "Set CLIJECT_BIN in the plugin script to the full path of cliject"
    exit 1
fi

ARGS=(column --xbar)

if [ -n "${CLIJECT_BOARD}" ]; then
    ARGS+=(--board "${CLIJECT_BOARD}")
fi
if [ -n "${CLIJECT_COLUMN}" ]; then
    ARGS+=("${CLIJECT_COLUMN}")
fi
if [ -n "${CLIJECT_ORG}" ]; then
    ARGS+=(--org "${CLIJECT_ORG}")
fi

OUTPUT=$("$CLIJECT" "${ARGS[@]}" 2>&1)
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo "cliject error | color=red"
    echo "---"
    echo "$OUTPUT"
else
    echo "$OUTPUT"
fi
