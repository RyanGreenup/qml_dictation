# Dictation justfile

# Default recipe - list available commands
default:
    @just --list

# Install the package
install:
    uv pip install --editable .

# Uninstall the package
uninstall:
    uv pip uninstall dictation

# Reinstall the package
reinstall: uninstall
    uv tool install . -U --refresh --force

# Run type checker
check:
    uv run -- pyright

# Run in development mode
dev:
    uv run -- python main.py serve

# Start the server
start:
    uv run -- python main.py start

# Toggle the window (requires running server)
toggle:
    uv run -- python main.py toggle

# Show server status
status:
    uv run -- python main.py status

# Stop the server
stop:
    uv run -- python main.py stop

# Install openrc service (requires sudo)
install-service:
    sudo cp openrc/dictation /etc/init.d/dictation
    sudo chmod +x /etc/init.d/dictation
    @echo "Service installed. Enable with: sudo rc-update add dictation default"

# Uninstall openrc service (requires sudo)
uninstall-service:
    -sudo rc-service dictation stop 2>/dev/null
    -sudo rc-update del dictation default 2>/dev/null
    sudo rm -f /etc/init.d/dictation
    @echo "Service uninstalled"

# Reinstall openrc service
reinstall-service: uninstall-service install-service

# Full install (package + service)
install-all: install install-service

# Full uninstall (service + package)
uninstall-all: uninstall-service uninstall

# Sync dependencies
sync:
    uv sync
