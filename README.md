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
### Overview

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

### Integration With Hyprland

Add something like this to the config and `s+a l` will trigger the palette.

```conf

# Notes mode - keybindings for note-taking workflow

# Database path for the palette server
$notes_db = ~/notes/notes.db

# Start palette server on login (if not already running)
exec-once = palette status || palette serve $notes_db &

# Enter notes submap with Super+N or Alt+F9
$map_name = notes
bind = $s, a, submap, $map_name
bind = ALT, F9, submap, $map_name

submap = $map_name

# l = link - toggle the link palette
bind = , l, exec, palette toggle
bind = , l, submap, reset

# Direct show/hide controls
bind = SHIFT, l, exec, palette show
bind = SHIFT, l, submap, reset

# Escape to exit submap without action
bind = , escape, submap, reset

submap = reset
# ...........................................................................

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
