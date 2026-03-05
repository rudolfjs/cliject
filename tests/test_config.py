import json

from cliject.config import get_default_board, get_default_view, load_config


def test_load_config_missing_file(monkeypatch, tmp_path):
    monkeypatch.setattr("cliject.config.CONFIG_PATH", tmp_path / "nonexistent.json")
    assert load_config() == {}


def test_load_config_valid_json(monkeypatch, tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"default_board": 5, "default_view": "list"}))
    monkeypatch.setattr("cliject.config.CONFIG_PATH", config_file)
    assert load_config() == {"default_board": 5, "default_view": "list"}


def test_get_default_board_no_org(monkeypatch, tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"default_board": 3}))
    monkeypatch.setattr("cliject.config.CONFIG_PATH", config_file)
    assert get_default_board() == 3


def test_get_default_board_with_org(monkeypatch, tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"orgs": {"myorg": {"default_board": 7}}}))
    monkeypatch.setattr("cliject.config.CONFIG_PATH", config_file)
    assert get_default_board(org="myorg") == 7


def test_get_default_board_org_missing(monkeypatch, tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"orgs": {"myorg": {"default_board": 7}}}))
    monkeypatch.setattr("cliject.config.CONFIG_PATH", config_file)
    assert get_default_board(org="otherorg") is None


def test_get_default_board_no_config(monkeypatch, tmp_path):
    monkeypatch.setattr("cliject.config.CONFIG_PATH", tmp_path / "nonexistent.json")
    assert get_default_board() is None


def test_get_default_view_default(monkeypatch, tmp_path):
    monkeypatch.setattr("cliject.config.CONFIG_PATH", tmp_path / "nonexistent.json")
    assert get_default_view() == "kanban"


def test_get_default_view_explicit(monkeypatch, tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"default_view": "list"}))
    monkeypatch.setattr("cliject.config.CONFIG_PATH", config_file)
    assert get_default_view() == "list"
