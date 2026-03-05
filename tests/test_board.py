import pytest

from cliject.board import _extract_status_options, _parse_item_node, _parse_project_node, fetch_board, fetch_projects
from cliject.models import Project, StatusOption


# ---------------------------------------------------------------------------
# _parse_project_node
# ---------------------------------------------------------------------------


def test_parse_project_node(sample_project_node):
    project = _parse_project_node(sample_project_node)
    assert isinstance(project, Project)
    assert project.id == "PVT_abc123"
    assert project.number == 1
    assert project.title == "My Project"
    assert project.short_description == "A test project"
    assert project.closed is False
    assert project.item_count == 5
    assert project.url == "https://github.com/orgs/myorg/projects/1"


def test_parse_project_node_missing_optional_fields():
    node = {"id": "PVT_1", "number": 2, "title": "Minimal"}
    project = _parse_project_node(node)
    assert project.short_description is None
    assert project.closed is False
    assert project.updated_at == ""
    assert project.url == ""
    assert project.item_count == 0


# ---------------------------------------------------------------------------
# _extract_status_options
# ---------------------------------------------------------------------------


def test_extract_status_options_found(sample_project_data):
    options, field_name = _extract_status_options(sample_project_data, "Status")
    assert field_name == "Status"
    assert len(options) == 3
    assert all(isinstance(o, StatusOption) for o in options)
    assert options[0].name == "Todo"
    assert options[1].color == "BLUE"
    assert options[2].name == "Done"


def test_extract_status_options_case_insensitive(sample_project_data):
    options, field_name = _extract_status_options(sample_project_data, "status")
    assert len(options) == 3
    assert field_name == "Status"


def test_extract_status_options_no_match():
    project_data = {"fields": {"nodes": [{"name": "Priority", "options": []}]}}
    options, field_name = _extract_status_options(project_data, "Status")
    assert options == []
    assert field_name == "Status"


def test_extract_status_options_empty_fields():
    options, field_name = _extract_status_options({}, "Status")
    assert options == []
    assert field_name == "Status"


# ---------------------------------------------------------------------------
# _parse_item_node
# ---------------------------------------------------------------------------


def test_parse_item_node_issue(sample_item_node_issue):
    item = _parse_item_node(sample_item_node_issue, "Status")
    assert item.item_type == "Issue"
    assert item.title == "Fix the bug"
    assert item.number == 42
    assert item.state == "OPEN"
    assert item.status == "In Progress"
    assert item.repo == "myorg/myrepo"
    assert len(item.assignees) == 1
    assert item.assignees[0].login == "alice"
    assert len(item.labels) == 1
    assert item.labels[0].name == "bug"


def test_parse_item_node_due_date(sample_item_node_issue):
    item = _parse_item_node(sample_item_node_issue, "Status")
    assert item.due_date == "2024-02-01"


def test_parse_item_node_pr(sample_item_node_pr):
    item = _parse_item_node(sample_item_node_pr, "Status")
    assert item.item_type == "PullRequest"
    assert item.title == "Add feature"
    assert item.number == 7
    assert item.status is None


def test_parse_item_node_draft(sample_item_node_draft):
    item = _parse_item_node(sample_item_node_draft, "Status")
    assert item.item_type == "DraftIssue"
    assert item.title == "Draft: explore options"
    assert item.number is None
    assert item.url is None
    assert item.state is None


def test_parse_item_node_no_content():
    node = {"id": "PVTI_x", "content": None, "fieldValues": {"nodes": []}}
    item = _parse_item_node(node, "Status")
    assert item.title == "(no title)"
    assert item.assignees == []
    assert item.labels == []


def test_parse_item_node_extra_fields():
    node = {
        "id": "PVTI_x",
        "content": {"__typename": "Issue", "title": "Test", "number": 1, "state": "OPEN"},
        "fieldValues": {
            "nodes": [
                {"field": {"name": "Estimate"}, "number": 3},
                {"field": {"name": "Notes"}, "text": "some note"},
            ]
        },
    }
    item = _parse_item_node(node, "Status")
    assert item.extra_fields["Estimate"] == 3
    assert item.extra_fields["Notes"] == "some note"
    assert item.status is None


def test_parse_item_node_non_due_date_field():
    node = {
        "id": "PVTI_x",
        "content": {"__typename": "Issue", "title": "Test", "number": 1, "state": "OPEN"},
        "fieldValues": {
            "nodes": [
                {"field": {"name": "Start Date"}, "date": "2024-01-01"},
            ]
        },
    }
    item = _parse_item_node(node, "Status")
    assert item.due_date is None
    assert item.extra_fields["Start Date"] == "2024-01-01"


# ---------------------------------------------------------------------------
# fetch_projects (mocked)
# ---------------------------------------------------------------------------


def test_fetch_projects_personal(mocker, sample_project_node):
    mocker.patch("cliject.board.get_token", return_value="token")
    mocker.patch("cliject.board.paginate_query", return_value=[sample_project_node])
    projects = fetch_projects()
    assert len(projects) == 1
    assert projects[0].title == "My Project"


def test_fetch_projects_org(mocker, sample_project_node):
    mocker.patch("cliject.board.get_token", return_value="token")
    mock_pq = mocker.patch("cliject.board.paginate_query", return_value=[sample_project_node])
    fetch_projects(org="myorg")
    call_args = mock_pq.call_args
    assert call_args[0][2] == {"org": "myorg"}


def test_fetch_projects_filters_none(mocker):
    mocker.patch("cliject.board.get_token", return_value="token")
    mocker.patch("cliject.board.paginate_query", return_value=[None, {"id": "1", "number": 2, "title": "Valid"}])
    projects = fetch_projects()
    assert len(projects) == 1
    assert projects[0].title == "Valid"


# ---------------------------------------------------------------------------
# fetch_board (mocked)
# ---------------------------------------------------------------------------


def test_fetch_board_column_grouping(mocker, sample_project_data, sample_item_node_issue):
    mocker.patch("cliject.board.get_token", return_value="token")
    mocker.patch("cliject.board.execute_query", return_value={"data": {"viewer": {"projectV2": sample_project_data}}})
    sample_item_node_issue["fieldValues"]["nodes"][0]["name"] = "Todo"
    mocker.patch("cliject.board.paginate_query", return_value=[sample_item_node_issue])

    board = fetch_board(project_number=1)
    assert board.project.title == "My Project"
    todo_col = next(c for c in board.columns if c.name == "Todo")
    assert len(todo_col.items) == 1
    assert todo_col.items[0].title == "Fix the bug"


def test_fetch_board_project_not_found(mocker):
    mocker.patch("cliject.board.get_token", return_value="token")
    mocker.patch("cliject.board.execute_query", return_value={"data": {"viewer": {"projectV2": {}}}})
    with pytest.raises(RuntimeError, match="not found"):
        fetch_board(project_number=999)


def test_fetch_board_no_status_items(mocker, sample_project_data):
    mocker.patch("cliject.board.get_token", return_value="token")
    mocker.patch("cliject.board.execute_query", return_value={"data": {"viewer": {"projectV2": sample_project_data}}})
    item_node = {
        "id": "PVTI_x",
        "content": {"__typename": "Issue", "title": "Orphan", "number": 99, "state": "OPEN"},
        "fieldValues": {"nodes": []},
    }
    mocker.patch("cliject.board.paginate_query", return_value=[item_node])

    board = fetch_board(project_number=1)
    assert len(board.no_status_items) == 1
    assert board.no_status_items[0].title == "Orphan"
