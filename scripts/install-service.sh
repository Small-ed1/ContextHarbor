#!/bin/bash
set -e

echo "CogniHub - Systemd Service Installation"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "This script must be run as root (use sudo)"
    exit 1
fi

SERVICE_FILE="/etc/systemd/system/cognihub.service"
SOURCE_SERVICE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/systemd/cognihub.service"

if [ ! -f "$SOURCE_SERVICE" ]; then
    echo "Error: cognihub.service not found at: $SOURCE_SERVICE"
    exit 1
fi

echo "Installing systemd service..."
cp "$SOURCE_SERVICE" "$SERVICE_FILE"
chmod 644 "$SERVICE_FILE"

echo "Reloading systemd..."
systemctl daemon-reload

echo "Enabling cognihub service..."
systemctl enable cognihub

echo ""
echo "Installation complete!"
echo ""
echo "Commands to manage the service:"
echo "  sudo systemctl start cognihub     # Start the service"
echo "  sudo systemctl stop cognihub      # Stop the service"
echo "  sudo systemctl restart cognihub   # Restart the service"
echo "  sudo systemctl status cognihub    # Check status"
echo "  sudo journalctl -u cognihub -f    # View logs"
echo ""
echo "Note: This unit expects a venv at %h/cognihub/.venv and your repo checked out to %h/cognihub"
echo "Note: Make sure Ollama is running (or install systemd/ollama-*.service separately)"
