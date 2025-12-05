# Lilium Palette justfile

# Default recipe - list available commands
default:
    @just --list

# Install the package
install:
    uv pip install --editable .

# Uninstall the package
uninstall:
    uv pip uninstall lilium-palette

# Reinstall the package
reinstall: uninstall install

# Run type checker
check:
    uv run -- pyright

# Create/recreate test database
test-db:
    uv run -- python scripts/create_test_db.py

# Run in development mode
dev db="test.db":
    uv run -- python main.py serve {{ db }}

# Toggle the palette (requires running server)
toggle:
    uv run -- python main.py toggle

# Show palette status
status:
    uv run -- python main.py status

# Stop the palette server
stop:
    uv run -- python main.py stop

# Install openrc service (requires sudo)
install-service:
    sudo cp openrc/lilium-palette /etc/init.d/lilium-palette
    sudo chmod +x /etc/init.d/lilium-palette
    @echo "Service installed. Enable with: sudo rc-update add lilium-palette default"

# Uninstall openrc service (requires sudo)
uninstall-service:
    -sudo rc-service lilium-palette stop 2>/dev/null
    -sudo rc-update del lilium-palette default 2>/dev/null
    sudo rm -f /etc/init.d/lilium-palette
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
