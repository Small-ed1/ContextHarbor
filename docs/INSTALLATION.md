# Installation Guide

This guide provides step-by-step instructions for installing and setting up Router Phase 1 on your system.

## Prerequisites

- Ubuntu 20.04 or later (or compatible Linux distribution)
- Python 3.8 or later
- At least 8GB RAM (16GB recommended)
- Ollama installed and running
- Git

## Quick Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd router_phase1
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Install System Dependencies

```bash
# Update package list
sudo apt update

# Install required packages
sudo apt install -y curl wget git python3 python3-pip python3-venv

# Install Ollama (if not already installed)
curl -fsSL https://ollama.ai/install.sh | sh
```

### 4. Configure Ollama

```bash
# Start Ollama service
sudo systemctl start ollama
sudo systemctl enable ollama

# Pull required models (adjust based on your needs)
ollama pull llama2:7b
ollama pull codellama:7b
```

### 5. Initial Setup

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Run initial setup
./scripts/setup-production.sh

# Or for development
make setup
```

### 6. Start Services

```bash
# Start the application
./start_servers.sh

# Or using systemd
sudo systemctl start router-phase1
```

### 7. Access the Application

- Web UI: http://localhost:8000
- API: http://localhost:8000/api/

## Detailed Installation

### Option A: Docker Installation

If you prefer Docker:

```bash
# Build the image
docker build -t router-phase1 .

# Run the container
docker run -d \
  --name router-phase1 \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  --restart unless-stopped \
  router-phase1
```

### Option B: Manual Installation

For manual setup:

1. **System Preparation**
   ```bash
   # Create dedicated user (optional)
   sudo useradd -m -s /bin/bash router
   sudo usermod -aG sudo router

   # Switch to user
   su - router
   ```

2. **Clone and Setup**
   ```bash
   git clone <repository-url> ~/router_phase1
   cd ~/router_phase1

   # Set up environment
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Database Setup**
   ```bash
   # Initialize database
   python3 -c "from backend.database import init_db; init_db()"
   ```

4. **Service Configuration**
   ```bash
   # Copy service files
   sudo cp config/router-phase1.service /etc/systemd/system/
   sudo cp config/router-phase1-backend.service /etc/systemd/system/

   # Reload systemd
   sudo systemctl daemon-reload

   # Enable services
   sudo systemctl enable router-phase1
   sudo systemctl enable router-phase1-backend
   ```

## Post-Installation

### Backup Setup

```bash
# Set up automated backups
sudo ./scripts/setup_backup_schedule.sh

# Test backup manually
python3 scripts/backup.py
```

### Health Check

```bash
# Check service status
sudo systemctl status router-phase1

# Check health endpoint
curl http://localhost:8000/api/health

# View logs
sudo journalctl -u router-phase1 -f
```

### Configuration

Edit `config.json` for custom settings:

```json
{
  "host": "0.0.0.0",
  "port": 8000,
  "ollama_host": "http://localhost:11434",
  "default_model": "llama2:7b",
  "max_context_tokens": 4096
}
```

## Troubleshooting

If installation fails, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues.

## Next Steps

- Configure your preferred models in Ollama
- Set up user authentication if needed
- Review security settings
- Configure monitoring and alerts