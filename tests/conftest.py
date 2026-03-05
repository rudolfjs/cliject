import pytest

from cliject.models import Assignee, Board, BoardColumn, BoardItem, Label, Project, StatusOption


@pytest.fixture
def sample_project_node():
    return {
        "id": "PVT_abc123",
        "number": 1,
        "title": "My Project",
        "shortDescription": "A test project",
        "closed": False,
        "updatedAt": "2024-01-15T10:00:00Z",
        "url": "https://github.com/orgs/myorg/projects/1",
        "items": {"totalCount": 5},
    }


@pytest.fixture
def sample_item_node_issue():
    return {
        "id": "PVTI_issue1",
        "content": {
            "__typename": "Issue",
            "title": "Fix the bug",
            "number": 42,
            "url": "https://github.com/myorg/myrepo/issues/42",
            "state": "OPEN",
            "repository": {"nameWithOwner": "myorg/myrepo"},
            "assignees": {"nodes": [{"login": "alice", "avatarUrl": "https://avatars.example.com/alice"}]},
            "labels": {"nodes": [{"name": "bug", "color": "d73a4a"}]},
        },
        "fieldValues": {
            "nodes": [
                {"field": {"name": "Status"}, "name": "In Progress"},
                {"field": {"name": "Due Date"}, "date": "2024-02-01"},
            ]
        },
    }


@pytest.fixture
def sample_item_node_pr():
    return {
        "id": "PVTI_pr1",
        "content": {
            "__typename": "PullRequest",
            "title": "Add feature",
            "number": 7,
            "url": "https://github.com/myorg/myrepo/pull/7",
            "state": "OPEN",
            "repository": {"nameWithOwner": "myorg/myrepo"},
            "assignees": {"nodes": []},
            "labels": {"nodes": []},
        },
        "fieldValues": {"nodes": []},
    }


@pytest.fixture
def sample_item_node_draft():
    return {
        "id": "PVTI_draft1",
        "content": {
            "__typename": "DraftIssue",
            "title": "Draft: explore options",
            "assignees": {"nodes": []},
        },
        "fieldValues": {"nodes": []},
    }


@pytest.fixture
def sample_project_data():
    return {
        "id": "PVT_abc123",
        "number": 1,
        "title": "My Project",
        "shortDescription": "A test project",
        "closed": False,
        "updatedAt": "2024-01-15T10:00:00Z",
        "url": "https://github.com/orgs/myorg/projects/1",
        "items": {"totalCount": 5},
        "fields": {
            "nodes": [
                {
                    "name": "Status",
                    "options": [
                        {"id": "opt1", "name": "Todo", "color": "GRAY", "description": ""},
                        {"id": "opt2", "name": "In Progress", "color": "BLUE", "description": ""},
                        {"id": "opt3", "name": "Done", "color": "GREEN", "description": ""},
                    ],
                }
            ]
        },
    }


@pytest.fixture
def sample_board():
    project = Project(
        id="PVT_abc",
        number=1,
        title="Test Board",
        short_description="A board",
        closed=False,
        updated_at="2024-01-15T10:00:00Z",
        url="https://github.com/orgs/myorg/projects/1",
        item_count=2,
    )
    item = BoardItem(
        id="item1",
        item_type="Issue",
        title="Fix the bug",
        status="In Progress",
        number=42,
        url="https://github.com/myorg/myrepo/issues/42",
        state="OPEN",
        repo="myorg/myrepo",
        assignees=[Assignee(login="alice", avatar_url="")],
        labels=[Label(name="bug", color="d73a4a")],
    )
    columns = [
        BoardColumn(name="Todo", color="GRAY", items=[]),
        BoardColumn(name="In Progress", color="BLUE", items=[item]),
        BoardColumn(name="Done", color="GREEN", items=[]),
    ]
    return Board(project=project, columns=columns, no_status_items=[], status_field_name="Status")


@pytest.fixture
def sample_status_options():
    return [
        StatusOption(id="opt1", name="Todo", color="GRAY"),
        StatusOption(id="opt2", name="In Progress", color="BLUE"),
        StatusOption(id="opt3", name="Done", color="GREEN"),
    ]
