import subprocess

import pytest
from typer.testing import CliRunner

from cliject.main import app
from cliject.models import Assignee, Board, BoardColumn, BoardItem, Label, Project

runner = CliRunner()


def _make_project(**kwargs) -> Project:
    defaults = dict(
        id="PVT_1",
        number=1,
        title="My Project",
        short_description=None,
        closed=False,
        updated_at="2024-01-15T10:00:00Z",
        url="https://github.com/orgs/myorg/projects/1",
        item_count=3,
    )
    defaults.update(kwargs)
    return Project(**defaults)


def _make_board() -> Board:
    project = _make_project()
    item = BoardItem(
        id="item1",
        item_type="Issue",
        title="Fix bug",
        status="Todo",
        number=1,
        url="https://github.com/myorg/myrepo/issues/1",
        state="OPEN",
        repo="myorg/myrepo",
        assignees=[Assignee(login="alice", avatar_url="")],
        labels=[Label(name="bug", color="d73a4a")],
    )
    return Board(
        project=project,
        columns=[BoardColumn(name="Todo", color="GRAY", items=[item])],
        no_status_items=[],
        status_field_name="Status",
    )


# ---------------------------------------------------------------------------
# list command
# ---------------------------------------------------------------------------


def test_list_command_success(mocker):
    mocker.patch("cliject.main.fetch_projects", return_value=[_make_project()])
    mocker.patch("cliject.main.render_project_list")
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0


def test_list_command_no_projects(mocker):
    mocker.patch("cliject.main.fetch_projects", return_value=[])
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "No projects found" in result.output


def test_list_command_auth_error(mocker):
    mocker.patch("cliject.main.fetch_projects", side_effect=subprocess.CalledProcessError(1, "gh"))
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 1
    assert "gh CLI not authenticated" in result.output


def test_list_command_runtime_error(mocker):
    mocker.patch("cliject.main.fetch_projects", side_effect=RuntimeError("API failed"))
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 1
    assert "API failed" in result.output


# ---------------------------------------------------------------------------
# board command
# ---------------------------------------------------------------------------


def test_board_command_no_number_no_default(mocker):
    mocker.patch("cliject.main.get_default_board", return_value=None)
    result = runner.invoke(app, ["board"])
    assert result.exit_code == 1
    assert "no project number" in result.output.lower() or "default_board" in result.output


def test_board_command_invalid_view(mocker):
    mocker.patch("cliject.main.fetch_board", return_value=_make_board())
    mocker.patch("cliject.main.get_default_view", return_value="kanban")
    result = runner.invoke(app, ["board", "1", "--view", "grid"])
    assert result.exit_code == 1
    assert "kanban" in result.output or "list" in result.output


def test_board_command_success_kanban(mocker):
    mocker.patch("cliject.main.fetch_board", return_value=_make_board())
    mocker.patch("cliject.main.get_default_view", return_value="kanban")
    mock_render = mocker.patch("cliject.main.render_board")
    result = runner.invoke(app, ["board", "1"])
    assert result.exit_code == 0
    mock_render.assert_called_once()


def test_board_command_success_list_view(mocker):
    mocker.patch("cliject.main.fetch_board", return_value=_make_board())
    mocker.patch("cliject.main.get_default_view", return_value="kanban")
    mock_render = mocker.patch("cliject.main.render_board_list")
    result = runner.invoke(app, ["board", "1", "--view", "list"])
    assert result.exit_code == 0
    mock_render.assert_called_once()


def test_board_command_uses_config_default(mocker):
    mocker.patch("cliject.main.get_default_board", return_value=5)
    mocker.patch("cliject.main.fetch_board", return_value=_make_board())
    mocker.patch("cliject.main.get_default_view", return_value="kanban")
    mocker.patch("cliject.main.render_board")
    result = runner.invoke(app, ["board"])
    assert result.exit_code == 0


def test_board_command_auth_error(mocker):
    mocker.patch("cliject.main.get_default_board", return_value=1)
    mocker.patch("cliject.main.fetch_board", side_effect=subprocess.CalledProcessError(1, "gh"))
    result = runner.invoke(app, ["board"])
    assert result.exit_code == 1
    assert "gh CLI not authenticated" in result.output


def test_board_command_runtime_error(mocker):
    mocker.patch("cliject.main.get_default_board", return_value=1)
    mocker.patch("cliject.main.fetch_board", side_effect=RuntimeError("Project #1 not found"))
    result = runner.invoke(app, ["board"])
    assert result.exit_code == 1
    assert "not found" in result.output.lower()


@pytest.mark.parametrize("view", ["kanban", "list"])
def test_board_command_valid_views(mocker, view):
    mocker.patch("cliject.main.fetch_board", return_value=_make_board())
    mocker.patch("cliject.main.get_default_view", return_value="kanban")
    mocker.patch("cliject.main.render_board")
    mocker.patch("cliject.main.render_board_list")
    result = runner.invoke(app, ["board", "1", "--view", view])
    assert result.exit_code == 0
