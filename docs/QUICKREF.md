# Quick Reference - Background Servers

## Server Management Script

```bash
./servers.sh start    # Start all servers
./servers.sh stop     # Stop all servers
./servers.sh restart  # Restart all servers
./servers.sh status   # Check status
./servers.sh logs fastapi   # View FastAPI logs
./servers.sh logs ollama    # View Ollama logs
```

## Systemd Service (Optional)

```bash
sudo ./install-service.sh    # Install service
sudo systemctl start ollama-web
sudo systemctl stop ollama-web
sudo systemctl status ollama-web
sudo journalctl -u ollama-web -f
```

## Access

- App: http://localhost:8000
- Ollama API: http://localhost:11434

## Logs

- FastAPI: `tail -f fastapi.log`
- Ollama: `tail -f ollama.log`

## Current Status

Both servers running in background with PID tracking.
