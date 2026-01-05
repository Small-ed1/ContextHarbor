# Router Phase 1 - Production Deployment Guide

This guide explains how to deploy Router Phase 1 as a production service that starts automatically on boot.

## Prerequisites

- Linux system (Ubuntu/Debian/Arch)
- Python 3.8+
- Node.js 16+
- Ollama installed and running
- Root/sudo access for system configuration

### Arch Linux Dependencies

```bash
# Install required packages
sudo pacman -S python python-pip nodejs npm

# Note: On Arch Linux, Python packages are installed system-wide
# for production deployments to work with systemd services
```

## Quick Setup

Run the automated setup script:

```bash
chmod +x setup-production.sh
./setup-production.sh
```

This will:
- Create a dedicated `router` user
- Copy files to `/opt/router-phase1`
- Set up Python virtual environment
- Build the frontend
- Install and enable systemd service
- Start the application

## Manual Installation

If you prefer manual setup:

### 1. Create System User

```bash
sudo groupadd router
sudo useradd -r -s /bin/false -g router router
```

### 2. Install Dependencies

```bash
# Copy project to /opt
sudo mkdir -p /opt/router-phase1
sudo cp -r . /opt/router-phase1/
sudo chown -R router:router /opt/router-phase1

# Create virtual environment
sudo -u router python3 -m venv /opt/router-phase1/venv

# Install Python dependencies
sudo -u router bash -c "source /opt/router-phase1/venv/bin/activate && pip install -r /opt/router-phase1/requirements.txt"

# Build frontend
cd /opt/router-phase1/frontend
sudo -u router npm install
sudo -u router npm run build
```

### 3. Install Systemd Service

```bash
sudo cp router-phase1.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable router-phase1
sudo systemctl start router-phase1
```

## Ollama Setup

Router Phase 1 requires Ollama for LLM functionality. Set up Ollama to start on boot:

```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.ai/install.sh | sh

# Enable Ollama service (if available)
sudo systemctl enable ollama
sudo systemctl start ollama

# Pull required models
ollama pull llama3.2:1b
ollama pull llama3.2:3b
```

If you want Router Phase 1 to depend on Ollama, uncomment the dependency lines in `router-phase1.service`.

## Service Management

```bash
# Check status
sudo systemctl status router-phase1

# View logs
sudo journalctl -u router-phase1 -f

# Restart service
sudo systemctl restart router-phase1

# Stop service
sudo systemctl stop router-phase1

# Disable auto-start
sudo systemctl disable router-phase1
```

## Configuration

Environment variables can be modified in `/etc/systemd/system/router-phase1.service`:

- `OLLAMA_HOST`: Ollama server URL (default: http://127.0.0.1:11434)
- `OLLAMA_MODEL`: Default model to use
- `OLLAMA_MODEL_LARGE`: Model for complex tasks

After changes, reload systemd and restart:

```bash
sudo systemctl daemon-reload
sudo systemctl restart router-phase1
```

## Monitoring

The service includes:
- Automatic restarts on failure
- Resource limits (2GB memory, 200% CPU)
- Journal logging
- Health checks via `/api/health`

Monitor with:
```bash
# System logs
sudo journalctl -u router-phase1 -f

# Resource usage
sudo systemctl status router-phase1
```

## Troubleshooting

### Service Won't Start
Check logs:
```bash
sudo journalctl -u router-phase1 -n 50
```

Common issues:
- Missing Python dependencies
- Ollama not running
- Port 8000 already in use
- Permission issues

### Frontend Not Loading
Ensure the build completed:
```bash
cd /opt/router-phase1/frontend
sudo -u router npm run build
sudo systemctl restart router-phase1
```

### API Errors
Check Ollama status:
```bash
sudo systemctl status ollama
ollama list
```

## Security Notes

- Service runs as unprivileged `router` user
- No new privileges allowed
- Home directory protected
- Kernel modules protected
- Resource limits enforced

## Updates

To update the application:

```bash
# Stop service
sudo systemctl stop router-phase1

# Update code
sudo cp -r /path/to/new/code/* /opt/router-phase1/

# Rebuild frontend if changed
cd /opt/router-phase1/frontend
sudo -u router npm install
sudo -u router npm run build

# Restart service
sudo systemctl start router-phase1
```