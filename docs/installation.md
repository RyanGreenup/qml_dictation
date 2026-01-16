# Dictation Installation Guide

A voice dictation tool using local Whisper for speech-to-text transcription.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- PipeWire or PulseAudio (for audio capture)
- Wayland compositor (tested with Hyprland)

## Install the Package

```bash
# From the project directory
uv tool install . --force

# Or from a specific path
uv tool install /path/to/dictation --force
```

This installs the `dictation` CLI to `~/.local/bin/`.

## Set Up Systemd User Service

The service runs the dictation server in the background, listening for toggle commands.

```bash
# Create user systemd directory if it doesn't exist
mkdir -p ~/.config/systemd/user

# Copy the service file
cp dictation.service ~/.config/systemd/user/

# Reload systemd
systemctl --user daemon-reload

# Enable and start the service
systemctl --user enable --now dictation
```

## Configure Hyprland Keybinding

Add to your Hyprland config (e.g., `~/.config/hypr/hyprland.conf` or a sourced file):

```conf
# Toggle dictation overlay with SUPER+SHIFT+D
bind = $s SHIFT, d, exec, dictation toggle
```

Then reload Hyprland:

```bash
hyprctl reload
```

## Verify Installation

```bash
# Check service status
systemctl --user status dictation

# Check if server is responding
dictation status
```

## Usage

1. Press `SUPER + SHIFT + D` to show the overlay
2. Click "Start Recording" or press `V` to begin dictation
3. Speak into your microphone
4. Press the button or `V` again to stop and transcribe
5. Text is automatically copied to clipboard
6. Press `Esc` to close the overlay

## Configuration

### Whisper Model

Set the `DICTATION_MODEL` environment variable to change the model size:

```bash
# In your shell profile or systemd service override
export DICTATION_MODEL=small  # Options: tiny, base, small, medium, large-v3
```

Default is `base` (~74MB, good balance of speed/accuracy).

To override in systemd:

```bash
systemctl --user edit dictation
```

Add:

```ini
[Service]
Environment="DICTATION_MODEL=small"
```

## Troubleshooting

### Check Logs

```bash
journalctl --user -u dictation -f
```

### First Run Downloads Model

The first transcription downloads the Whisper model (~74MB for base). This may take a moment.

### Microphone Not Working

- Ensure PipeWire/PulseAudio is running
- Check microphone permissions: `pactl list sources`
- Test with: `arecord -d 3 test.wav && aplay test.wav`

### Service Won't Start

```bash
# Check for errors
journalctl --user -u dictation --no-pager

# Try running manually
dictation serve
```

### IPC Connection Failed

If `dictation toggle` says "Failed to toggle - is the server running?":

```bash
# Check socket exists
ls /tmp/dictation-$(id -u).sock

# Restart service
systemctl --user restart dictation
```

## Uninstall

```bash
# Stop and disable service
systemctl --user disable --now dictation

# Remove service file
rm ~/.config/systemd/user/dictation.service
systemctl --user daemon-reload

# Remove package
uv tool uninstall dictation
```
