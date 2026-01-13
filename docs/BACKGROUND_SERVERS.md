# Background Server Management

All servers can run in the background without active monitoring. Two options are available:

## Option 1: Manual Control (Recommended for Development)

Use the `servers.sh` script for full manual control:

```bash
# Start all servers
./servers.sh start

# Stop all servers
./servers.sh stop

# Restart all servers
./servers.sh restart

# Check status
./servers.sh status

# View logs
./servers.sh logs fastapi
./servers.sh logs ollama
```

**Features:**
- Simple bash script with no dependencies
- PID tracking and clean shutdown
- Log files (fastapi.log, ollama.log)
- Health checks on startup
- Easy status monitoring

## Option 2: Systemd Service (Production)

Install as systemd service for automatic startup:

```bash
sudo ./install-service.sh

# Then manage with systemctl:
sudo systemctl start ollama-web
sudo systemctl stop ollama-web
sudo systemctl status ollama-web
sudo journalctl -u ollama-web -f
```

**Features:**
- Automatic startup on boot
- Automatic restart on failure
- Managed by system init
- Integrated with system logs

## Current Server Status

Both servers are currently running:

- **FastAPI**: http://localhost:8000 (PID tracked)
- **Ollama**: http://localhost:11434 (PID tracked)

## Log Files

- `fastapi.log` - FastAPI server output
- `ollama.log` - Ollama server output

View logs anytime:
```bash
tail -f fastapi.log
tail -f ollama.log
```

## Quick Start

1. Ensure dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Pull embedding model for RAG:
   ```bash
   ollama pull embeddinggemma
   ```

3. Start servers:
   ```bash
   ./servers.sh start
   ```

4. Access the app: http://localhost:8000

## Notes

- Both options run servers completely in background
- No need to monitor terminal or keep windows open
- Logs are captured and can be viewed anytime
- Processes are tracked and can be stopped cleanly
