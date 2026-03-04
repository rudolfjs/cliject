import subprocess
from pathlib import Path
from typing import Optional

import typer

from .board import fetch_board, fetch_projects
from .config import get_default_board
from .render import render_board, render_project_list

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

    render_board(b, show_empty=show_empty)
