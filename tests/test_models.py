from cliject.models import Assignee, Board, BoardColumn, BoardItem, Label, Project, StatusOption


def test_board_item_defaults():
    item = BoardItem(id="1", item_type="Issue", title="Test")
    assert item.status is None
    assert item.number is None
    assert item.url is None
    assert item.state is None
    assert item.repo is None
    assert item.due_date is None
    assert item.assignees == []
    assert item.labels == []
    assert item.extra_fields == {}


def test_board_item_mutable_default_isolation():
    item1 = BoardItem(id="1", item_type="Issue", title="A")
    item2 = BoardItem(id="2", item_type="Issue", title="B")
    item1.assignees.append(Assignee(login="alice", avatar_url=""))
    assert item2.assignees == []


def test_board_item_extra_fields_isolation():
    item1 = BoardItem(id="1", item_type="Issue", title="A")
    item2 = BoardItem(id="2", item_type="Issue", title="B")
    item1.extra_fields["key"] = "value"
    assert "key" not in item2.extra_fields


def test_status_option_description_default():
    opt = StatusOption(id="opt1", name="Todo", color="GRAY")
    assert opt.description == ""


def test_board_column_items_isolation():
    col1 = BoardColumn(name="A", color="GRAY")
    col2 = BoardColumn(name="B", color="BLUE")
    col1.items.append(BoardItem(id="1", item_type="Issue", title="X"))
    assert col2.items == []


def test_label_construction():
    label = Label(name="bug", color="d73a4a")
    assert label.name == "bug"
    assert label.color == "d73a4a"


def test_project_optional_fields():
    p = Project(
        id="PVT_1",
        number=1,
        title="Proj",
        short_description=None,
        closed=False,
        updated_at="2024-01-01",
        url="",
        item_count=0,
    )
    assert p.short_description is None


def test_board_construction(sample_board):
    assert sample_board.project.title == "Test Board"
    assert len(sample_board.columns) == 3
    assert sample_board.status_field_name == "Status"
