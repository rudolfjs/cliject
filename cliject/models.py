from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Label:
    name: str
    color: str  # 6-char hex from GitHub (no leading #)


@dataclass
class Assignee:
    login: str
    avatar_url: str


@dataclass
class BoardItem:
    id: str
    item_type: str  # "Issue", "PullRequest", "DraftIssue"
    title: str
    status: Optional[str] = None
    number: Optional[int] = None
    url: Optional[str] = None
    state: Optional[str] = None  # "OPEN", "CLOSED", "MERGED"
    repo: Optional[str] = None
    assignees: list[Assignee] = field(default_factory=list)
    labels: list[Label] = field(default_factory=list)
    due_date: Optional[str] = None
    extra_fields: dict = field(default_factory=dict)


@dataclass
class StatusOption:
    id: str
    name: str
    color: str  # GitHub constant: GRAY/BLUE/GREEN/YELLOW/ORANGE/RED/PINK/PURPLE
    description: str = ""


@dataclass
class BoardColumn:
    name: str
    color: str
    items: list[BoardItem] = field(default_factory=list)


@dataclass
class Project:
    id: str
    number: int
    title: str
    short_description: Optional[str]
    closed: bool
    updated_at: str
    url: str
    item_count: int


@dataclass
class Board:
    project: Project
    columns: list[BoardColumn]
    no_status_items: list[BoardItem]
    status_field_name: str
