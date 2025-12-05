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
   lilium-palette serve
   lilium-palette toggle
   lilium-palette stop
   ```

## Usage
### Overview

Start the server:

```bash
lilium-palette serve /path/to/notes.db
```

Control from another terminal:

```bash
lilium-palette toggle   # show/hide
lilium-palette show
lilium-palette hide
lilium-palette stop
lilium-palette status
```

### Integration With Hyprland

Add something like this to the config and `s+a l` will trigger the palette.

```conf

# Notes mode - keybindings for note-taking workflow

# Database path for the palette server
$notes_db = ~/notes/notes.db

# Start palette server on login (if not already running)
exec-once = lilium-palette status || lilium-palette serve $notes_db &

# Enter notes submap with Super+N or Alt+F9
$map_name = notes
bind = $s, a, submap, $map_name
bind = ALT, F9, submap, $map_name

submap = $map_name

# l = link - toggle the link palette
bind = , l, exec, lilium-palette toggle
bind = , l, submap, reset

# Direct show/hide controls
bind = SHIFT, l, exec, lilium-palette show
bind = SHIFT, l, submap, reset

# Escape to exit submap without action
bind = , escape, submap, reset

submap = reset
# ...........................................................................

```

### Systemd

Install the service:

```bash
cp lilium-palette.service ~/.config/systemd/user/
# Edit the service file to set your database path
systemctl --user daemon-reload
systemctl --user enable --now lilium-palette
```

Control:

```bash
systemctl --user status lilium-palette
systemctl --user restart lilium-palette
journalctl --user -u lilium-palette -f
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
