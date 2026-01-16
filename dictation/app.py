"""Qt Application and QML engine setup."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QUrl, Slot
from PySide6.QtGui import QClipboard, QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from dictation.controller import DictationController
from dictation.ipc import IPCServer

if TYPE_CHECKING:
    pass


class ClipboardHelper(QObject):
    """Helper class to expose clipboard functionality to QML."""

    def __init__(self, clipboard: QClipboard, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._clipboard = clipboard

    @Slot(str)
    def copy(self, text: str) -> None:
        """Copy text to clipboard."""
        self._clipboard.setText(text)


class DictationApp:
    """Main dictation application."""

    def __init__(self) -> None:
        self._app: QGuiApplication | None = None
        self._engine: QQmlApplicationEngine | None = None
        self._ipc_server: IPCServer | None = None
        self._clipboard_helper: ClipboardHelper | None = None
        self._dictation_controller: DictationController | None = None

    def run(self) -> int:
        """Run the application. Returns exit code."""
        self._app = QGuiApplication(sys.argv)
        self._app.setApplicationName("Dictation")
        self._app.setOrganizationName("Dictation")

        # Set up clipboard helper and dictation controller
        clipboard = self._app.clipboard()
        if clipboard is not None:
            self._clipboard_helper = ClipboardHelper(clipboard)
            self._dictation_controller = DictationController(clipboard)

        # Set up IPC server
        self._ipc_server = IPCServer()
        self._ipc_server.toggle_requested.connect(self._toggle_window)
        self._ipc_server.show_requested.connect(self._show_window)
        self._ipc_server.hide_requested.connect(self._hide_window)
        self._ipc_server.quit_requested.connect(self._quit_app)

        if not self._ipc_server.start():
            print("Warning: Failed to start IPC server", file=sys.stderr)

        # Set up QML engine
        self._engine = QQmlApplicationEngine()

        # Register context properties
        root_context = self._engine.rootContext()
        root_context.setContextProperty("clipboard", self._clipboard_helper)
        root_context.setContextProperty("dictation", self._dictation_controller)

        # Load QML
        qml_file = Path(__file__).parent / "qml" / "Main.qml"
        self._engine.load(QUrl.fromLocalFile(str(qml_file)))

        if not self._engine.rootObjects():
            print("Failed to load QML", file=sys.stderr)
            return 1

        # Run event loop
        exit_code = self._app.exec()

        # Cleanup
        if self._ipc_server is not None:
            self._ipc_server.stop()

        return exit_code

    def _get_root_window(self) -> QObject | None:
        """Get the root window object."""
        if self._engine is None:
            return None
        root_objects = self._engine.rootObjects()
        if root_objects:
            return root_objects[0]
        return None

    @Slot()
    def _toggle_window(self) -> None:
        """Toggle window visibility."""
        window = self._get_root_window()
        if window is None:
            return

        is_visible = window.property("visible")
        if is_visible:
            window.setProperty("visible", False)
        else:
            window.setProperty("visible", True)

    @Slot()
    def _show_window(self) -> None:
        """Show the window."""
        window = self._get_root_window()
        if window is not None:
            window.setProperty("visible", True)

    @Slot()
    def _hide_window(self) -> None:
        """Hide the window."""
        window = self._get_root_window()
        if window is not None:
            window.setProperty("visible", False)

    @Slot()
    def _quit_app(self) -> None:
        """Quit the application."""
        if self._app is not None:
            self._app.quit()
