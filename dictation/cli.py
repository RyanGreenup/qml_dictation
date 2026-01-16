"""Dictation CLI entry point."""

from __future__ import annotations

import sys

import typer

app = typer.Typer(
    name="dictation",
    help="Dictation application.",
)


@app.command()
def serve() -> None:
    """Start the dictation server."""
    from dictation.app import DictationApp

    dictation_app = DictationApp()
    sys.exit(dictation_app.run())


@app.command()
def toggle() -> None:
    """Toggle window visibility via IPC."""
    from dictation.ipc import send_toggle

    if send_toggle():
        typer.echo("Toggled window")
    else:
        typer.echo("Failed to toggle - is the server running?", err=True)
        raise typer.Exit(1)


@app.command()
def show() -> None:
    """Show the window via IPC."""
    from dictation.ipc import send_show

    if send_show():
        typer.echo("Showing window")
    else:
        typer.echo("Failed to show - is the server running?", err=True)
        raise typer.Exit(1)


@app.command()
def hide() -> None:
    """Hide the window via IPC."""
    from dictation.ipc import send_hide

    if send_hide():
        typer.echo("Hiding window")
    else:
        typer.echo("Failed to hide - is the server running?", err=True)
        raise typer.Exit(1)


@app.command()
def stop() -> None:
    """Stop the dictation server."""
    from dictation.ipc import send_stop

    if send_stop():
        typer.echo("Stopped dictation server")
    else:
        typer.echo("Failed to stop - is the server running?", err=True)
        raise typer.Exit(1)


@app.command()
def status() -> None:
    """Check if the dictation server is running."""
    from dictation.ipc import is_server_running

    if is_server_running():
        typer.echo("Dictation server is running")
    else:
        typer.echo("Dictation server is not running")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
