import json
from pathlib import Path
from typing import Optional

CONFIG_PATH = Path.home() / ".config" / "cliject" / "config.json"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    with CONFIG_PATH.open() as f:
        return json.load(f)


def get_default_board(org: Optional[str] = None) -> Optional[int]:
    config = load_config()
    if org:
        return config.get("orgs", {}).get(org, {}).get("default_board")
    return config.get("default_board")
