# Server Management

All servers can be started in the background without monitoring using the `servers.sh` script.

## Usage

```bash
# Start all servers (FastAPI + Ollama)
./servers.sh start

# Stop all servers
./servers.sh stop

# Restart all servers
./servers.sh restart

# Check server status
./servers.sh status

# View logs
./servers.sh logs fastapi    # View FastAPI logs
./servers.sh logs ollama     # View Ollama logs
```

## Servers

- **FastAPI**: http://localhost:8000
- **Ollama**: http://localhost:11434

## Logs

Logs are written to:
- `fastapi.log` - FastAPI server logs
- `ollama.log` - Ollama server logs

## Process Management

The script manages PIDs automatically:
- `fastapi.pid` - FastAPI process ID
- `ollama.pid` - Ollama process ID

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Pull an embedding model for RAG:
   ```bash
   ollama pull embeddinggemma
   ```

3. Start servers:
   ```bash
   ./servers.sh start
   ```

## Notes

- Both servers run as background processes with nohup
- Logs are captured and can be viewed with `tail -f`
- Status can be checked anytime with `./servers.sh status`
- Servers are automatically stopped/restarted by the script
