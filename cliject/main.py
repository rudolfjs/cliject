import subprocess
from pathlib import Path
from typing import Optional

import typer

from .board import fetch_board, fetch_projects
from .config import get_default_board, get_default_column, get_default_view
from .render import render_board, render_board_list, render_project_list

app = typer.Typer(
    name="cliject",
    help="GitHub Projects V2 terminal board viewer",
    no_args_is_help=True,
)


@app.command(name="list")
def list_projects(
    org: Optional[str] = typer.Option(None, "--org", "-o", help="GitHub organization login"),
    closed: bool = typer.Option(False, "--closed", help="Include closed projects"),
) -> None:
    """List GitHub Projects V2 (personal or org)."""
    try:
        projects = fetch_projects(org=org)
    except subprocess.CalledProcessError:
        typer.echo("Error: gh CLI not authenticated. Run: gh auth login", err=True)
        raise typer.Exit(1)
    except RuntimeError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

    if not projects:
        typer.echo("No projects found.")
        return
    render_project_list(projects, show_closed=closed)


@app.command()
def board(
    number: Optional[int] = typer.Argument(None, help="Project number (uses config default if omitted)"),
    org: Optional[str] = typer.Option(None, "--org", "-o", help="GitHub organization login"),
    group_by: str = typer.Option("Status", "--group-by", "-g", help="Field name to group by"),
    show_empty: bool = typer.Option(False, "--show-empty", help="Show columns with no items"),
    me: bool = typer.Option(False, "--me", help="Only show items assigned to me"),
    view: Optional[str] = typer.Option(None, "--view", "-v", help="Display style: kanban or list (overrides config)"),
) -> None:
    """Render a project as a Kanban board."""
    if number is None:
        number = get_default_board(org=org)
    if number is None:
        scope = f"orgs.{org}" if org else "top-level"
        typer.echo(
            f"Error: no project number given and no default_board set for {scope} "
            f"in {Path.home() / '.config' / 'cliject' / 'config.json'}",
            err=True,
        )
        raise typer.Exit(1)
    try:
        b = fetch_board(project_number=number, org=org, group_by_field=group_by, assigned_to_me=me)
    except subprocess.CalledProcessError:
        typer.echo("Error: gh CLI not authenticated. Run: gh auth login", err=True)
        raise typer.Exit(1)
    except RuntimeError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

    resolved_view = view or get_default_view()
    if resolved_view not in ("kanban", "list"):
        typer.echo(f"Error: --view must be 'kanban' or 'list', got '{resolved_view}'", err=True)
        raise typer.Exit(1)

    if resolved_view == "list":
        render_board_list(b, show_empty=show_empty)
    else:
        render_board(b, show_empty=show_empty)


@app.command()
def column(
    column_name: Optional[str] = typer.Argument(None, help="Column name to display (uses config default_column if omitted)"),
    number: Optional[int] = typer.Option(None, "--board", "-b", help="Project number (uses config default if omitted)"),
    org: Optional[str] = typer.Option(None, "--org", "-o", help="GitHub organization login"),
    group_by: str = typer.Option("Status", "--group-by", "-g", help="Field name to group by"),
    xbar: bool = typer.Option(False, "--xbar", help="Output in xbar/SwiftBar plugin format"),
) -> None:
    """Display items from a single board column (for widgets and scripts)."""
    if number is None:
        number = get_default_board(org=org)
    if number is None:
        scope = f"orgs.{org}" if org else "top-level"
        typer.echo(
            f"Error: no project number given and no default_board set for {scope} "
            f"in {Path.home() / '.config' / 'cliject' / 'config.json'}",
            err=True,
        )
        raise typer.Exit(1)

    if column_name is None:
        column_name = get_default_column(org=org)
    if column_name is None:
        typer.echo(
            f"Error: no column name given and no default_column set "
            f"in {Path.home() / '.config' / 'cliject' / 'config.json'}",
            err=True,
        )
        raise typer.Exit(1)

    try:
        b = fetch_board(project_number=number, org=org, group_by_field=group_by)
    except subprocess.CalledProcessError:
        typer.echo("Error: gh CLI not authenticated. Run: gh auth login", err=True)
        raise typer.Exit(1)
    except RuntimeError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

    matched = next((c for c in b.columns if c.name.lower() == column_name.lower()), None)
    if matched is None:
        available = ", ".join(f'"{c.name}"' for c in b.columns)
        typer.echo(f"Error: column '{column_name}' not found. Available: {available}", err=True)
        raise typer.Exit(1)

    if xbar:
        typer.echo(f"{matched.name} ({len(matched.items)})")
        typer.echo("---")
        for item in matched.items:
            line = item.title
            if item.url:
                line += f" | href={item.url}"
            typer.echo(line)
    else:
        for item in matched.items:
            typer.echo(item.title)
