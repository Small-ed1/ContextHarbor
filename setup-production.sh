#!/bin/bash
# Router Phase 1 Installation and Setup Script
# This script sets up the Router Phase 1 application for production use

set -e

echo "🔧 Router Phase 1 Setup Script"
echo "=============================="

# Check for required tools
echo "🔍 Checking prerequisites..."
command -v python3 >/dev/null 2>&1 || { echo "❌ Python3 is required but not installed. Please install python."; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed. Please install nodejs and npm."; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "❌ npm is required but not installed. Please install nodejs and npm."; exit 1; }

echo "✅ Prerequisites check passed"

# Check if we have sudo access (but allow running as root)
if [[ $EUID -ne 0 ]] && ! sudo -n true 2>/dev/null; then
   echo "❌ This script requires sudo access. Please run with sudo or ensure you have sudo privileges."
   exit 1
fi

# Configuration
PROJECT_DIR="/opt/router-phase1"
SERVICE_NAME="router-phase1"
VENV_DIR="$PROJECT_DIR/venv"
# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$SCRIPT_DIR"

echo "📁 Project directory: $PROJECT_DIR"
echo "🔧 Virtual environment: $VENV_DIR"
echo "📂 Source directory: $SOURCE_DIR"

# Create dedicated user and group
echo "👤 Creating dedicated user and group..."
sudo groupadd -f router
sudo useradd -r -s /bin/false -g router router 2>/dev/null || true

# Copy project to installation directory
echo "📋 Copying project files..."
sudo mkdir -p "$PROJECT_DIR"
sudo cp -r "$SOURCE_DIR"/* "$PROJECT_DIR"/
sudo chown -R router:router "$PROJECT_DIR"
sudo chmod -R 755 "$PROJECT_DIR"

# Install Python dependencies system-wide (Arch Linux approach)
echo "📦 Installing Python dependencies system-wide..."
sudo pip install --break-system-packages -r "$PROJECT_DIR/requirements.txt"

# Create a simple wrapper script for the application
echo "📝 Creating application wrapper..."
cat > "$PROJECT_DIR/run.sh" << 'EOF'
#!/bin/bash
export PYTHONPATH=/opt/router-phase1
cd /opt/router-phase1
exec uvicorn backend.app:app --host 0.0.0.0 --port 8000 --workers 2
EOF
chmod +x "$PROJECT_DIR/run.sh"

# Build frontend
echo "⚛️ Building frontend..."
cd "$PROJECT_DIR/frontend"
sudo npm install
sudo npm run build

# Install Ollama service (optional)
read -p "🔍 Do you want to set up Ollama systemd service? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🦙 Installing Ollama systemd service..."
    sudo cp "$PROJECT_DIR/ollama.service" /etc/systemd/system/
    sudo systemctl enable ollama
    sudo systemctl start ollama
    echo "⏳ Waiting for Ollama to start..."
    sleep 5
fi

# Copy Router Phase 1 systemd service file
echo "🔄 Installing Router Phase 1 systemd service..."
sudo cp "$PROJECT_DIR/router-phase1.service" /etc/systemd/system/
sudo systemctl daemon-reload

# Enable and start the service
echo "🚀 Enabling and starting service..."
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl start "$SERVICE_NAME"

# Check service status
echo "📊 Checking service status..."
sudo systemctl status "$SERVICE_NAME" --no-pager

echo ""
echo "✅ Setup complete!"
echo ""
echo "Service management commands:"
echo "  Start:   sudo systemctl start $SERVICE_NAME"
echo "  Stop:    sudo systemctl stop $SERVICE_NAME"
echo "  Restart: sudo systemctl restart $SERVICE_NAME"
echo "  Status:  sudo systemctl status $SERVICE_NAME"
echo "  Logs:    sudo journalctl -u $SERVICE_NAME -f"
echo ""
echo "The application should now be running at http://localhost:8000"
echo "Make sure Ollama is running and accessible."