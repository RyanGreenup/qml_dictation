#!/usr/bin/env python3
"""Create a test database with sample data for development."""

from __future__ import annotations

import sqlite3
import uuid
from pathlib import Path


def create_database(db_path: Path) -> None:
    """Create the test database with schema and sample data."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create folders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS folders (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            parent_id TEXT,
            user_id TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES folders(id) ON DELETE CASCADE
        )
    """)

    # Create notes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            abstract TEXT,
            content TEXT NOT NULL,
            syntax TEXT NOT NULL DEFAULT 'md',
            parent_id TEXT,
            user_id TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES folders(id) ON DELETE CASCADE
        )
    """)

    # Create the view for path mapping
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_note_id_path_mapping AS
        WITH RECURSIVE folder_path AS (
            SELECT
                id,
                title,
                parent_id,
                user_id,
                title AS path
            FROM folders
            WHERE parent_id IS NULL

            UNION ALL

            SELECT
                f.id,
                f.title,
                f.parent_id,
                f.user_id,
                fp.path || '/' || f.title AS path
            FROM folders f
            INNER JOIN folder_path fp ON f.parent_id = fp.id
        )
        SELECT
            n.id,
            n.title,
            n.syntax,
            n.user_id,
            CASE
                WHEN n.parent_id IS NULL THEN n.title || '.' || n.syntax
                ELSE fp.path || '/' || n.title || '.' || n.syntax
            END AS full_path
        FROM notes n
        LEFT JOIN folder_path fp ON n.parent_id = fp.id
    """)

    # Insert sample folders
    user_id = "test-user"

    folders = [
        (str(uuid.uuid4().hex), "projects", None, user_id),
        (str(uuid.uuid4().hex), "journal", None, user_id),
        (str(uuid.uuid4().hex), "reference", None, user_id),
    ]

    cursor.executemany(
        "INSERT INTO folders (id, title, parent_id, user_id) VALUES (?, ?, ?, ?)",
        folders,
    )

    # Get folder IDs
    cursor.execute("SELECT id, title FROM folders")
    folder_map = {row[1]: row[0] for row in cursor.fetchall()}

    # Add subfolders
    subfolders = [
        (str(uuid.uuid4().hex), "python", folder_map["projects"], user_id),
        (str(uuid.uuid4().hex), "rust", folder_map["projects"], user_id),
        (str(uuid.uuid4().hex), "2024", folder_map["journal"], user_id),
        (str(uuid.uuid4().hex), "2025", folder_map["journal"], user_id),
    ]

    cursor.executemany(
        "INSERT INTO folders (id, title, parent_id, user_id) VALUES (?, ?, ?, ?)",
        subfolders,
    )

    # Update folder map
    cursor.execute("SELECT id, title FROM folders")
    folder_map = {row[1]: row[0] for row in cursor.fetchall()}

    # Insert sample notes
    notes = [
        # Root level notes
        (uuid.uuid4().hex, "readme", "Project readme", "# Readme\n\nThis is a test.", "md", None, user_id),
        (uuid.uuid4().hex, "todo", "Things to do", "- [ ] Task 1\n- [ ] Task 2", "md", None, user_id),
        # Project notes
        (uuid.uuid4().hex, "palette", "Palette project notes", "# Palette\n\nLink palette app.", "md", folder_map["python"], user_id),
        (uuid.uuid4().hex, "fastapi-app", "FastAPI project", "# FastAPI App\n\nREST API.", "md", folder_map["python"], user_id),
        (uuid.uuid4().hex, "cli-tool", "Rust CLI tool", "# CLI Tool\n\nCommand line tool in Rust.", "md", folder_map["rust"], user_id),
        # Journal notes
        (uuid.uuid4().hex, "01-15", "January 15 journal", "Today I worked on...", "md", folder_map["2024"], user_id),
        (uuid.uuid4().hex, "01-16", "January 16 journal", "Continued working...", "md", folder_map["2024"], user_id),
        (uuid.uuid4().hex, "12-01", "December 1 journal", "Starting the month...", "md", folder_map["2025"], user_id),
        (uuid.uuid4().hex, "12-04", "December 4 journal", "Building palette app...", "md", folder_map["2025"], user_id),
        # Reference notes
        (uuid.uuid4().hex, "vim-shortcuts", "Vim shortcuts reference", "# Vim Shortcuts\n\n- `:w` save\n- `:q` quit", "md", folder_map["reference"], user_id),
        (uuid.uuid4().hex, "git-commands", "Git commands reference", "# Git Commands\n\n- `git status`\n- `git add`", "md", folder_map["reference"], user_id),
        (uuid.uuid4().hex, "sql-reference", "SQL reference", "# SQL\n\n- SELECT\n- INSERT", "md", folder_map["reference"], user_id),
    ]

    cursor.executemany(
        "INSERT INTO notes (id, title, abstract, content, syntax, parent_id, user_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
        notes,
    )

    conn.commit()
    conn.close()

    print(f"Created test database at {db_path}")

    # Verify the view works
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, full_path FROM v_note_id_path_mapping ORDER BY full_path")
    print("\nSample data:")
    for row in cursor.fetchall():
        print(f"  [{row[1]}][{row[0][:8]}...] -> {row[2]}")
    conn.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        db_path = Path(sys.argv[1])
    else:
        db_path = Path(__file__).parent.parent / "test.db"

    # Remove existing test database
    if db_path.exists():
        db_path.unlink()

    create_database(db_path)
