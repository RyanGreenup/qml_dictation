"""IPC server and client for dictation toggle functionality."""

from __future__ import annotations

import os
import socket
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QSocketNotifier, Signal

if TYPE_CHECKING:
    pass


def get_socket_path() -> Path:
    """Get the socket path for IPC communication."""
    uid = os.getuid()
    return Path(f"/tmp/dictation-{uid}.sock")


class IPCServer(QObject):
    """Unix domain socket server for IPC commands."""

    toggle_requested = Signal()
    show_requested = Signal()
    hide_requested = Signal()
    quit_requested = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._socket: socket.socket | None = None
        self._notifier: QSocketNotifier | None = None

    def start(self) -> bool:
        """Start the IPC server. Returns True on success."""
        socket_path = get_socket_path()

        # Remove existing socket if present
        if socket_path.exists():
            socket_path.unlink()

        try:
            self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self._socket.setblocking(False)
            self._socket.bind(str(socket_path))
            self._socket.listen(5)

            # Set up Qt notification for incoming connections
            self._notifier = QSocketNotifier(
                self._socket.fileno(),
                QSocketNotifier.Type.Read,
                self,
            )
            self._notifier.activated.connect(self._handle_connection)

            return True
        except OSError as e:
            print(f"Failed to start IPC server: {e}")
            return False

    def stop(self) -> None:
        """Stop the IPC server."""
        if self._notifier is not None:
            self._notifier.setEnabled(False)
            self._notifier = None

        if self._socket is not None:
            self._socket.close()
            self._socket = None

        socket_path = get_socket_path()
        if socket_path.exists():
            socket_path.unlink()

    def _handle_connection(self) -> None:
        """Handle an incoming connection."""
        if self._socket is None:
            return

        try:
            conn, _ = self._socket.accept()
            with conn:
                conn.settimeout(1.0)
                data = conn.recv(64).decode("utf-8").strip()
                self._process_command(data)
                conn.sendall(b"OK\n")
        except (OSError, TimeoutError):
            pass

    def _process_command(self, command: str) -> None:
        """Process a received command."""
        cmd = command.upper()
        if cmd == "TOGGLE":
            self.toggle_requested.emit()
        elif cmd == "SHOW":
            self.show_requested.emit()
        elif cmd == "HIDE":
            self.hide_requested.emit()
        elif cmd == "QUIT" or cmd == "STOP":
            self.quit_requested.emit()


def send_command(command: str, timeout: float = 1.0) -> bool:
    """Send a command to the dictation server. Returns True on success."""
    socket_path = get_socket_path()

    if not socket_path.exists():
        return False

    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect(str(socket_path))
            sock.sendall(f"{command}\n".encode("utf-8"))
            response = sock.recv(64).decode("utf-8").strip()
            return response == "OK"
    except (OSError, TimeoutError):
        return False


def send_toggle() -> bool:
    """Send a toggle command to the dictation server."""
    return send_command("TOGGLE")


def send_show() -> bool:
    """Send a show command to the dictation server."""
    return send_command("SHOW")


def send_hide() -> bool:
    """Send a hide command to the dictation server."""
    return send_command("HIDE")


def send_stop() -> bool:
    """Send a stop command to the dictation server."""
    return send_command("STOP")


def is_server_running() -> bool:
    """Check if the dictation server is running."""
    return send_command("PING")
