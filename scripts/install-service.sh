#!/bin/bash
set -e

echo "Ollama Web RAG - Systemd Service Installation"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "This script must be run as root (use sudo)"
    exit 1
fi

SERVICE_FILE="/etc/systemd/system/ollama-web.service"
SOURCE_SERVICE="ollama-web.service"

if [ ! -f "$SOURCE_SERVICE" ]; then
    echo "Error: $SOURCE_SERVICE not found in current directory"
    exit 1
fi

echo "Installing systemd service..."
cp "$SOURCE_SERVICE" "$SERVICE_FILE"
chmod 644 "$SERVICE_FILE"

echo "Reloading systemd..."
systemctl daemon-reload

echo "Enabling ollama-web service..."
systemctl enable ollama-web

echo ""
echo "Installation complete!"
echo ""
echo "Commands to manage the service:"
echo "  sudo systemctl start ollama-web     # Start the service"
echo "  sudo systemctl stop ollama-web      # Stop the service"
echo "  sudo systemctl restart ollama-web   # Restart the service"
echo "  sudo systemctl status ollama-web    # Check status"
echo "  sudo journalctl -u ollama-web -f   # View logs"
echo ""
echo "Note: Make sure Ollama is running or also set up as a systemd service"
