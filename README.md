# Palette

Search notes, insert markdown links.

## Install

1. From Remote

   ```bash
   uv tool install 'git+https://github.com/ryangreenup/<TODO>'
   ```

2. Local

   ```bash
   uv tool install .
   palette serve
   palette toggle
   palette stop
   ```

## Usage

Start the server:

```bash
palette serve /path/to/notes.db
```

Control from another terminal:

```bash
palette toggle   # show/hide
palette show
palette hide
palette stop
palette status
```

## Keybindings

| Key     | Action                     |
| ------- | -------------------------- |
| Up/Down | Navigate results           |
| Enter   | Copy link, close           |
| Escape  | Close                      |
| Tab     | Toggle ID/path link format |

## Link Formats

- **ID**: `[Title][note-id]`
- **Path**: `[Title][/path/to/note]`

## Database

Requires SQLite with `v_note_id_path_mapping` view containing `id`, `title`, `full_path` columns.
