"""Data models and SQLite search functionality."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import Any

from PySide6.QtCore import (
    QAbstractListModel,
    QByteArray,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    Qt,
    Signal,
    Slot,
)


@dataclass(frozen=True, slots=True)
class NoteResult:
    """A note search result."""

    id: str
    title: str
    full_path: str

    def to_markdown_link(self) -> str:
        """Return the markdown link format [title][id]."""
        return f"[{self.title}][{self.id}]"

    def to_markdown_link_by_path(self) -> str:
        """Return the markdown link format [title][path]."""
        return f"[{self.title}][{self.full_path}]"


class NoteRole(IntEnum):
    """Custom roles for the note model."""

    Id = Qt.ItemDataRole.UserRole + 1
    Title = Qt.ItemDataRole.UserRole + 2
    FullPath = Qt.ItemDataRole.UserRole + 3
    MarkdownLink = Qt.ItemDataRole.UserRole + 4
    MarkdownLinkByPath = Qt.ItemDataRole.UserRole + 5


def search_notes(
    db_path: Path, query: str, limit: int = 50, candidate_limit: int = 500
) -> list[NoteResult]:
    """Search notes by path using fuzzy matching.

    Uses a two-phase approach for performance:
    1. SQL pre-filter with subsequence pattern to reduce candidates
    2. Python fuzzy scoring to rank and sort results
    """
    from palette.fuzzy import build_sql_pattern, rank_matches

    if not query.strip():
        return []

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        # Phase 1: SQL pre-filter with subsequence pattern
        search_pattern = build_sql_pattern(query)
        cursor.execute(
            """
            SELECT id, title, full_path
            FROM v_note_id_path_mapping
            WHERE LOWER(full_path) LIKE ? ESCAPE '\\'
            ORDER BY full_path
            LIMIT ?
            """,
            (search_pattern, candidate_limit),
        )
        candidates = [
            NoteResult(id=row[0], title=row[1], full_path=row[2])
            for row in cursor.fetchall()
        ]
    finally:
        conn.close()

    # Phase 2: Fuzzy scoring and ranking
    ranked = rank_matches(
        query=query,
        items=candidates,
        key=lambda note: note.full_path,
        limit=limit,
    )

    return [note for note, _score in ranked]


class NoteSearchModel(QAbstractListModel):
    """Qt model for note search results."""

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._results: list[NoteResult] = []
        self._db_path: Path | None = None

    def set_db_path(self, path: Path) -> None:
        """Set the database path for searches."""
        self._db_path = path

    def rowCount(
        self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()
    ) -> int:
        """Return the number of results."""
        if parent.isValid():
            return 0
        return len(self._results)

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        """Return data for the given index and role."""
        if not index.isValid() or index.row() >= len(self._results):
            return None

        result = self._results[index.row()]

        if role == Qt.ItemDataRole.DisplayRole or role == NoteRole.FullPath:
            return result.full_path
        if role == NoteRole.Id:
            return result.id
        if role == NoteRole.Title:
            return result.title
        if role == NoteRole.MarkdownLink:
            return result.to_markdown_link()
        if role == NoteRole.MarkdownLinkByPath:
            return result.to_markdown_link_by_path()

        return None

    def roleNames(self) -> dict[int, QByteArray]:
        """Return role names for QML access."""
        return {
            NoteRole.Id: QByteArray(b"noteId"),
            NoteRole.Title: QByteArray(b"noteTitle"),
            NoteRole.FullPath: QByteArray(b"fullPath"),
            NoteRole.MarkdownLink: QByteArray(b"markdownLink"),
            NoteRole.MarkdownLinkByPath: QByteArray(b"markdownLinkByPath"),
        }

    @Slot(str)
    def search(self, query: str) -> None:
        """Perform a search and update results."""
        if self._db_path is None:
            return

        self.beginResetModel()
        self._results = search_notes(self._db_path, query)
        self.endResetModel()

    @Slot(int, result=str)
    def getMarkdownLink(self, row: int) -> str:
        """Get the markdown link for a specific row."""
        if 0 <= row < len(self._results):
            return self._results[row].to_markdown_link()
        return ""

    @Slot(int, result=str)
    def getMarkdownLinkByPath(self, row: int) -> str:
        """Get the markdown link by path for a specific row."""
        if 0 <= row < len(self._results):
            return self._results[row].to_markdown_link_by_path()
        return ""

    resultCountChanged = Signal()

    @property
    def resultCount(self) -> int:
        """Return the number of results."""
        return len(self._results)
