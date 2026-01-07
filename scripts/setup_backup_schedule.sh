#!/bin/bash
# Setup automated backup schedule for Router Phase 1

set -e

echo "Setting up automated backups for Router Phase 1..."

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root (sudo)"
   exit 1
fi

PROJECT_DIR="/home/small_ed/router_phase1"
SERVICE_FILE="$PROJECT_DIR/config/router-backup.service"
TIMER_FILE="$PROJECT_DIR/config/router-backup.timer"

# Check if files exist
if [[ ! -f "$SERVICE_FILE" ]]; then
    echo "Error: Service file not found at $SERVICE_FILE"
    exit 1
fi

if [[ ! -f "$TIMER_FILE" ]]; then
    echo "Error: Timer file not found at $TIMER_FILE"
    exit 1
fi

# Copy service and timer files
cp "$SERVICE_FILE" /etc/systemd/system/
cp "$TIMER_FILE" /etc/systemd/system/

# Reload systemd
systemctl daemon-reload

# Enable and start the timer
systemctl enable router-backup.timer
systemctl start router-backup.timer

echo "Automated backup setup completed!"
echo "Backup will run daily at 2:00 AM"
echo "Check status with: systemctl status router-backup.timer"
echo "View logs with: journalctl -u router-backup.service"