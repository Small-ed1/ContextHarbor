#!/bin/bash
# Quick Setup Script for Router Phase 1 Auto-Start Management

echo "🚀 Router Phase 1 Auto-Start Setup"
echo "=================================="

PROJECT_ROOT="$(dirname "$0")"
cd "$PROJECT_ROOT"

echo "📁 Project Root: $PROJECT_ROOT"

# Function to check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        echo "🔐 Running with root privileges"
        return 0
    else
        echo "⚠️  Running without root privileges - some features limited"
        return 1
    fi
}

# Check current status
echo ""
echo "📊 Current Service Status:"
python auto_server_manager.py status

# Install auto-start service
echo ""
echo "🔧 Installing systemd service for auto-start on boot..."

if check_root; then
    # Install as root
    cp /tmp/router-auto-manager.service /etc/systemd/system/
    systemctl daemon-reload
    systemctl enable router-auto-manager.service
    
    echo "✅ Auto-start service installed and enabled"
    echo ""
    echo "🚀 Starting auto-manager now..."
    systemctl start router-auto-manager.service
    
    sleep 3
    echo ""
    echo "📋 Service Status:"
    systemctl status router-auto-manager.service --no-pager -l
    
    echo ""
    echo "✅ Auto-start setup complete!"
    echo "📝 Logs: sudo journalctl -u router-auto-manager -f"
    
else
    echo "❌ Root privileges required for auto-start installation"
    echo "🔐 Please run with sudo: sudo ./setup_autostart.sh"
    echo ""
    echo "🔧 Manual setup commands:"
    echo "   sudo cp /tmp/router-auto-manager.service /etc/systemd/system/"
    echo "   sudo systemctl daemon-reload"
    echo "   sudo systemctl enable router-auto-manager.service"
    echo "   sudo systemctl start router-auto-manager.service"
fi

echo ""
echo "🎯 Final Verification:"
echo "🏠 Local URLs:"
echo "   Frontend: http://localhost:1234"
echo "   Backend:  http://localhost:8000"
echo ""
echo "🔗 Network URLs:"
python network_access.py | grep -A 5 "Tailscale Network Access"

echo ""
echo "✅ Setup complete!"