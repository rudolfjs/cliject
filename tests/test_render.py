import cliject.render as render_mod
from rich.console import Console as RichConsole

from cliject.models import Assignee, Board, BoardColumn, BoardItem, Label, Project
from cliject.render import (
    _render_item,
    _render_item_list,
    _rich_color,
    render_board,
    render_project_list,
)


def _make_item(**kwargs) -> BoardItem:
    defaults = dict(id="item1", item_type="Issue", title="Fix the bug", state="OPEN")
    defaults.update(kwargs)
    return BoardItem(**defaults)


def _make_project(**kwargs) -> Project:
    defaults = dict(
        id="PVT_1",
        number=1,
        title="My Project",
        short_description="A test project",
        closed=False,
        updated_at="2024-01-15T10:00:00Z",
        url="https://github.com/orgs/myorg/projects/1",
        item_count=5,
    )
    defaults.update(kwargs)
    return Project(**defaults)


# ---------------------------------------------------------------------------
# _rich_color
# ---------------------------------------------------------------------------


def test_rich_color_known():
    assert _rich_color("GREEN") == "green"
    assert _rich_color("BLUE") == "blue"
    assert _rich_color("RED") == "red"


def test_rich_color_unknown():
    assert _rich_color("UNKNOWN") == "white"
    assert _rich_color("") == "white"


def test_rich_color_case_insensitive():
    assert _rich_color("gray") == "bright_black"


# ---------------------------------------------------------------------------
# _render_item
# ---------------------------------------------------------------------------


def test_render_item_basic():
    item = _make_item()
    t = _render_item(item)
    plain = t.plain
    assert "[I]" in plain
    assert "Fix the bug" in plain


def test_render_item_pr_badge():
    item = _make_item(item_type="PullRequest")
    t = _render_item(item)
    assert "[PR]" in t.plain


def test_render_item_draft_badge():
    item = _make_item(item_type="DraftIssue", state=None)
    t = _render_item(item)
    assert "[D]" in t.plain


def test_render_item_closed_has_strike_style():
    item = _make_item(state="CLOSED")
    t = _render_item(item)
    # Verify the text object has a span with strike style
    styles = [str(span.style) for span in t._spans]
    assert any("strike" in s for s in styles)


def test_render_item_truncation():
    long_title = "A" * 35
    item = _make_item(title=long_title)
    t = _render_item(item)
    plain = t.plain
    # Truncated to 30 + ellipsis character
    assert "A" * 30 + "…" in plain
    assert "A" * 31 not in plain


def test_render_item_no_truncation_exact_30():
    title = "B" * 30
    item = _make_item(title=title)
    t = _render_item(item)
    assert title in t.plain
    assert "…" not in t.plain


def test_render_item_with_assignees():
    item = _make_item(assignees=[Assignee(login="alice", avatar_url="")])
    t = _render_item(item)
    assert "@alice" in t.plain


def test_render_item_with_labels():
    item = _make_item(labels=[Label(name="bug", color="d73a4a")])
    t = _render_item(item)
    assert "bug" in t.plain


def test_render_item_with_due_date():
    item = _make_item(due_date="2024-03-01")
    t = _render_item(item)
    assert "due: 2024-03-01" in t.plain


def test_render_item_with_repo_and_number():
    item = _make_item(repo="myorg/myrepo", number=42)
    t = _render_item(item)
    assert "myrepo#42" in t.plain


# ---------------------------------------------------------------------------
# _render_item_list
# ---------------------------------------------------------------------------


def test_render_item_list_format():
    item = _make_item(title="My task")
    t = _render_item_list(item)
    plain = t.plain
    assert "•" in plain
    assert "[I]" in plain
    assert "My task" in plain


def test_render_item_list_no_truncation():
    long_title = "A" * 50
    item = _make_item(title=long_title)
    t = _render_item_list(item)
    assert long_title in t.plain


# ---------------------------------------------------------------------------
# render_project_list (console capture)
# ---------------------------------------------------------------------------


def test_render_project_list(monkeypatch):
    test_console = RichConsole(record=True, width=120)
    monkeypatch.setattr(render_mod, "console", test_console)
    projects = [_make_project(), _make_project(id="PVT_2", number=2, title="Second Project", closed=True)]
    render_project_list(projects, show_closed=False)
    output = test_console.export_text()
    assert "My Project" in output
    assert "Second Project" not in output  # closed, filtered out


def test_render_project_list_show_closed(monkeypatch):
    test_console = RichConsole(record=True, width=120)
    monkeypatch.setattr(render_mod, "console", test_console)
    projects = [_make_project(closed=True)]
    render_project_list(projects, show_closed=True)
    output = test_console.export_text()
    assert "My Project" in output


# ---------------------------------------------------------------------------
# render_board empty columns
# ---------------------------------------------------------------------------


def test_render_board_empty_columns_hidden(monkeypatch):
    test_console = RichConsole(record=True, width=200)
    monkeypatch.setattr(render_mod, "console", test_console)
    project = _make_project()
    board = Board(
        project=project,
        columns=[BoardColumn(name="Todo", color="GRAY", items=[])],
        no_status_items=[],
        status_field_name="Status",
    )
    render_board(board, show_empty=False)
    output = test_console.export_text()
    assert "No columns to display" in output


def test_render_board_empty_columns_shown(monkeypatch):
    test_console = RichConsole(record=True, width=200)
    monkeypatch.setattr(render_mod, "console", test_console)
    project = _make_project()
    item = _make_item()
    board = Board(
        project=project,
        columns=[
            BoardColumn(name="Todo", color="GRAY", items=[]),
            BoardColumn(name="Done", color="GREEN", items=[item]),
        ],
        no_status_items=[],
        status_field_name="Status",
    )
    render_board(board, show_empty=True)
    output = test_console.export_text()
    assert "Todo" in output
    assert "Done" in output
