"""Link palette CLI entry point."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated

import typer

app = typer.Typer(
    name="lilium-palette",
    help="Link palette for searching notes and generating markdown links.",
)


@app.command()
def serve(
    db: Annotated[
        Path,
        typer.Argument(
            help="Path to the SQLite database file",
            exists=True,
            dir_okay=False,
            resolve_path=True,
        ),
    ],
) -> None:
    """Start the palette server."""
    from palette.app import PaletteApp

    palette_app = PaletteApp(db)
    sys.exit(palette_app.run())


@app.command()
def toggle() -> None:
    """Toggle palette visibility via IPC."""
    from palette.ipc import send_toggle

    if send_toggle():
        typer.echo("Toggled palette")
    else:
        typer.echo("Failed to toggle - is the server running?", err=True)
        raise typer.Exit(1)


@app.command()
def show() -> None:
    """Show the palette via IPC."""
    from palette.ipc import send_show

    if send_show():
        typer.echo("Showing palette")
    else:
        typer.echo("Failed to show - is the server running?", err=True)
        raise typer.Exit(1)


@app.command()
def hide() -> None:
    """Hide the palette via IPC."""
    from palette.ipc import send_hide

    if send_hide():
        typer.echo("Hiding palette")
    else:
        typer.echo("Failed to hide - is the server running?", err=True)
        raise typer.Exit(1)


@app.command()
def stop() -> None:
    """Stop the palette server."""
    from palette.ipc import send_stop

    if send_stop():
        typer.echo("Stopped palette server")
    else:
        typer.echo("Failed to stop - is the server running?", err=True)
        raise typer.Exit(1)


@app.command()
def status() -> None:
    """Check if the palette server is running."""
    from palette.ipc import is_server_running

    if is_server_running():
        typer.echo("Palette server is running")
    else:
        typer.echo("Palette server is not running")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
