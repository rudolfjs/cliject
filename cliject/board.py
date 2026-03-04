from typing import Optional

from .auth import get_token, get_viewer_login
from .api import execute_query, paginate_query
from .queries import (
    LIST_VIEWER_PROJECTS,
    LIST_ORG_PROJECTS,
    GET_PROJECT_FIELDS,
    GET_PROJECT_ITEMS,
)
from .models import (
    Assignee,
    Board,
    BoardColumn,
    BoardItem,
    Label,
    Project,
    StatusOption,
)


def _parse_project_node(node: dict) -> Project:
    return Project(
        id=node["id"],
        number=node["number"],
        title=node["title"],
        short_description=node.get("shortDescription"),
        closed=node.get("closed", False),
        updated_at=node.get("updatedAt", ""),
        url=node.get("url", ""),
        item_count=node.get("items", {}).get("totalCount", 0),
    )


def fetch_projects(org: Optional[str] = None) -> list[Project]:
    token = get_token()
    if org:
        nodes = paginate_query(
            token,
            LIST_ORG_PROJECTS,
            {"org": org},
            ["organization", "projectsV2"],
        )
    else:
        nodes = paginate_query(
            token,
            LIST_VIEWER_PROJECTS,
            {},
            ["viewer", "projectsV2"],
        )
    return [_parse_project_node(n) for n in nodes if n]


def _get_project_data(token: str, number: int, org: Optional[str]) -> dict:
    is_org = bool(org)
    variables = {
        "owner": org or "",
        "number": number,
        "isOrg": is_org,
    }
    data = execute_query(token, GET_PROJECT_FIELDS, variables)
    root = data.get("data", {})
    if is_org:
        return root.get("organization", {}).get("projectV2", {})
    return root.get("viewer", {}).get("projectV2", {})


def _extract_status_options(
    project_data: dict, group_by_field: str
) -> tuple[list[StatusOption], str]:
    """Return (status_options, field_name). field_name is the matched field name."""
    fields_nodes = project_data.get("fields", {}).get("nodes", [])
    for field_node in fields_nodes:
        if not field_node:
            continue
        name = field_node.get("name", "")
        if name.lower() == group_by_field.lower() and "options" in field_node:
            options = [
                StatusOption(
                    id=opt["id"],
                    name=opt["name"],
                    color=opt.get("color", "GRAY"),
                    description=opt.get("description", ""),
                )
                for opt in field_node.get("options", [])
            ]
            return options, name
    return [], group_by_field


def _parse_item_node(node: dict, status_field_name: str) -> BoardItem:
    content = node.get("content") or {}
    typename = content.get("__typename", "")

    # Determine item type
    if "number" in content and content.get("state") is not None:
        # Check if it's a PR by presence of merged state or type hint
        # GitHub API returns state MERGED for PRs, OPEN/CLOSED for both
        # We use the typename if available, else heuristic
        if typename == "PullRequest":
            item_type = "PullRequest"
        else:
            item_type = "Issue"
    elif typename == "DraftIssue" or (not content.get("url") and content.get("title")):
        item_type = "DraftIssue"
    else:
        item_type = "Issue"

    title = content.get("title", "(no title)")
    number = content.get("number")
    url = content.get("url")
    state = content.get("state")
    repo = content.get("repository", {}).get("nameWithOwner") if content.get("repository") else None

    assignees = [
        Assignee(login=a["login"], avatar_url=a.get("avatarUrl", ""))
        for a in (content.get("assignees") or {}).get("nodes", [])
        if a
    ]
    labels = [
        Label(name=lb["name"], color=lb.get("color", "ffffff"))
        for lb in (content.get("labels") or {}).get("nodes", [])
        if lb
    ]

    # Parse field values
    status = None
    due_date = None
    extra_fields: dict = {}

    for fv in node.get("fieldValues", {}).get("nodes", []):
        if not fv:
            continue
        field_info = fv.get("field") or {}
        field_name = field_info.get("name", "")

        if "name" in fv and field_name.lower() == status_field_name.lower():
            status = fv["name"]
        elif "date" in fv:
            if field_name.lower() in ("due date", "due", "deadline"):
                due_date = fv["date"]
            else:
                extra_fields[field_name] = fv["date"]
        elif "text" in fv:
            extra_fields[field_name] = fv["text"]
        elif "number" in fv:
            extra_fields[field_name] = fv["number"]

    return BoardItem(
        id=node["id"],
        item_type=item_type,
        title=title,
        status=status,
        number=number,
        url=url,
        state=state,
        repo=repo,
        assignees=assignees,
        labels=labels,
        due_date=due_date,
        extra_fields=extra_fields,
    )


def fetch_board(
    project_number: int,
    org: Optional[str] = None,
    group_by_field: str = "Status",
    assigned_to_me: bool = False,
) -> Board:
    token = get_token()
    is_org = bool(org)

    # 1. Fetch project metadata + field definitions
    project_data = _get_project_data(token, project_number, org)
    if not project_data:
        raise RuntimeError(f"Project #{project_number} not found.")

    project = _parse_project_node(project_data)
    status_options, status_field_name = _extract_status_options(project_data, group_by_field)

    # 2. Paginate all items
    variables = {
        "owner": org or "",
        "number": project_number,
        "isOrg": is_org,
    }

    if is_org:
        items_path = ["organization", "projectV2", "items"]
    else:
        items_path = ["viewer", "projectV2", "items"]

    raw_items = paginate_query(token, GET_PROJECT_ITEMS, variables, items_path)

    # 3. Parse items
    parsed_items = [_parse_item_node(n, status_field_name) for n in raw_items if n]

    if assigned_to_me:
        viewer_login = get_viewer_login()
        parsed_items = [
            item for item in parsed_items
            if any(a.login == viewer_login for a in item.assignees)
        ]

    # 4. Group into columns
    column_map: dict[str, BoardColumn] = {}
    for opt in status_options:
        column_map[opt.name] = BoardColumn(name=opt.name, color=opt.color, items=[])

    no_status_items: list[BoardItem] = []

    for item in parsed_items:
        if item.status and item.status in column_map:
            column_map[item.status].items.append(item)
        else:
            no_status_items.append(item)

    # Maintain order from status_options
    columns = [column_map[opt.name] for opt in status_options]

    return Board(
        project=project,
        columns=columns,
        no_status_items=no_status_items,
        status_field_name=status_field_name,
    )
