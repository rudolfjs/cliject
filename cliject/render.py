from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .models import Board, BoardItem, Project

console = Console()

GITHUB_COLOR_MAP = {
    "GRAY": "bright_black",
    "BLUE": "blue",
    "GREEN": "green",
    "YELLOW": "yellow",
    "ORANGE": "dark_orange",
    "RED": "red",
    "PINK": "hot_pink",
    "PURPLE": "medium_purple",
}

ITEM_TYPE_BADGE = {
    "Issue": "[I]",
    "PullRequest": "[PR]",
    "DraftIssue": "[D]",
}


def _rich_color(github_color: str) -> str:
    return GITHUB_COLOR_MAP.get(github_color.upper(), "white")


def _render_item(item: BoardItem) -> Text:
    is_closed = item.state in ("CLOSED", "MERGED")

    t = Text()

    # Type badge
    badge = ITEM_TYPE_BADGE.get(item.item_type, "[?]")
    badge_style = "dim" if is_closed else "bold"
    t.append(badge, style=badge_style)
    t.append(" ")

    # Title (truncated, linked if URL available)
    title = item.title[:30] + ("…" if len(item.title) > 30 else "")
    title_style = "dim strike" if is_closed else ""
    if item.url:
        title_style = f"{title_style} link {item.url}".strip()
    t.append(title, style=title_style)
    t.append("\n")

    # Repo + number
    if item.repo and item.number is not None:
        short_repo = item.repo.split("/")[-1] if "/" in item.repo else item.repo
        t.append(f"  {short_repo}#{item.number}", style="dim cyan")
        t.append("\n")

    # Assignees
    if item.assignees:
        logins = " ".join(f"@{a.login}" for a in item.assignees)
        t.append(f"  {logins}", style="dim green")
        t.append("\n")

    # Labels
    if item.labels:
        for label in item.labels:
            hex_color = label.color if label.color else "ffffff"
            t.append(f" {label.name} ", style=f"bold on #{hex_color}")
            t.append(" ")
        t.append("\n")

    # Due date
    if item.due_date:
        t.append(f"  due: {item.due_date}", style="dim yellow")
        t.append("\n")

    return t


def _render_column_panel(col_name: str, col_color: str, items: list[BoardItem]) -> Panel:
    rich_color = _rich_color(col_color)
    content = Text()
    for item in items:
        content.append_text(_render_item(item))
        content.append("─" * 38 + "\n", style="dim")

    count = len(items)
    title = f"[bold {rich_color}]{col_name}[/] [dim]({count})[/]"
    return Panel(content, title=title, width=42, expand=False)


def render_project_list(projects: list[Project], show_closed: bool = False) -> None:
    filtered = [p for p in projects if show_closed or not p.closed]

    table = Table(
        title="GitHub Projects V2",
        show_header=True,
        header_style="bold magenta",
        expand=False,
    )
    table.add_column("#", style="dim", width=6)
    table.add_column("Title", min_width=30)
    table.add_column("Items", justify="right", width=6)
    table.add_column("Status", width=8)
    table.add_column("Updated", width=12)

    for p in filtered:
        num = str(p.number)
        title = p.title
        if p.short_description:
            title += f"\n[dim]{p.short_description[:60]}[/dim]"
        items = str(p.item_count)
        status = "[dim]closed[/dim]" if p.closed else "[green]open[/green]"
        updated = p.updated_at[:10] if p.updated_at else ""
        row_style = "dim" if p.closed else ""
        table.add_row(num, title, items, status, updated, style=row_style)

    console.print(table)


def render_board(board: Board, show_empty: bool = False) -> None:
    project = board.project
    console.print(
        f"\n[bold]{project.title}[/bold]  "
        f"[dim]#{project.number} · {project.item_count} items · "
        f"updated {project.updated_at[:10]}[/dim]",
    )
    if project.short_description:
        console.print(f"[dim]{project.short_description}[/dim]")
    console.print()

    panels = []
    for col in board.columns:
        if not show_empty and not col.items:
            continue
        panels.append(_render_column_panel(col.name, col.color, col.items))

    if panels:
        console.print(Columns(panels, equal=False, expand=False))
    else:
        console.print("[dim]No columns to display.[/dim]")

    if board.no_status_items:
        console.print(f"\n[bold dim]No {board.status_field_name}[/bold dim] ({len(board.no_status_items)} items)")
        no_status_text = Text()
        for item in board.no_status_items:
            no_status_text.append_text(_render_item(item))
            no_status_text.append("─" * 38 + "\n", style="dim")
        console.print(Panel(no_status_text, width=42, expand=False))
