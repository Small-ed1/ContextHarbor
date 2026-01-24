# CogniHub

A local-first AI assistant with chat, RAG, and deep research capabilities. Built with FastAPI, SQLite, and integrated with Ollama for local model execution.

## Features

- **Web Interface**: Modern chat UI with sidebar navigation, settings panel, and real-time updates
- **Chat Management**: Create, rename, archive, pin, and search through conversations
- **RAG System**: Document upload and retrieval-augmented generation for enhanced responses
- **Deep Research**: Multi-round research with web scraping, claim verification, and synthesis
- **Model Integration**: Auto-model selection, Ollama integration, and multiple model support
- **Terminal UI**: Textual-based TUI for console usage
- **Kiwix Integration**: Offline Wikipedia access through Kiwix server
- **Settings Management**: Per-chat settings for model, temperature, context, and more

## Tool Agent

For advanced interactions with Ollama using tool-calling, run the included agent:

```bash
./scripts/run_agent.sh
```

This provides a CLI interface with web search, document search, and safe terminal execution tools.
It expects the FastAPI server to be running and uses `API_BASE` (default `http://localhost:8000`).

## Quick Start

### Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) installed and running
- Required models: `llama3.1` and `nomic-embed-text`
- System: Linux (Arch/Ubuntu) or macOS (Windows support in development)

**Note**: The embedding model is `nomic-embed-text`, not `embeddinggemma`

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Small-ed1/CogniHub
   cd CogniHub
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Pull required Ollama models**
   ```bash
   ollama pull llama3.1
   ollama pull nomic-embed-text
   ```

4. **Set up Python environment** (if you encounter externally-managed-environment errors)
   ```bash
   # Option 1: Virtual environment (recommended)
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Option 2: System-wide install (development only)
   pip install -r requirements.txt --break-system-packages
   ```

### Running

#### Option 1: Web Interface (Recommended)

```bash
# Start the server
uvicorn src.cognihub.app:app --reload --host 0.0.0.0 --port 8000
```

Open http://localhost:8000 in your browser.

#### Option 2: Terminal UI

```bash
python src/cognihub/tui/cognihub_tui.py
```

#### Option 3: Production Deployment

```bash
# Install systemd services
sudo cp systemd/cognihub.service /etc/systemd/system/
sudo cp systemd/kiwix.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable cognihub kiwix
sudo systemctl start cognihub kiwix
```

## Architecture

### Backend (FastAPI)

- **Main Application**: `src/cognihub/app.py` - FastAPI server with all endpoints
- **Database Modules**:
  - `src/cognihub/stores/chatstore.py` - Chat and message management
  - `src/cognihub/stores/ragstore.py` - Document storage and embeddings
  - `src/cognihub/stores/webstore.py` - Web page caching and chunking
  - `src/cognihub/stores/researchstore.py` - Research run tracking and claims
- **Configuration**: `src/cognihub/config.py` - Environment variable handling

### Frontend

- **Web UI**: `static/index.html`, `static/app.js`, `static/styles.css`
- **Terminal UI**: `cognihub_tui.py` (Textual framework)

### Data Storage

- **SQLite Databases**:
  - `chat.sqlite3` - Conversations and messages
  - `rag.sqlite3` - Document embeddings and chunks
  - `web.sqlite3` - Web page cache
  - `research.sqlite3` - Research runs and results

## API Endpoints

### Chat Management
- `GET /api/chats` - List chats
- `POST /api/chats` - Create new chat
- `GET /api/chats/{id}` - Get chat details
- `PATCH /api/chats/{id}` - Update chat settings
- `DELETE /api/chats/{id}` - Delete chat

### Messages
- `POST /api/chats/{id}/append` - Add messages
- `POST /api/chats/{id}/clear` - Clear chat history
- `GET /api/chats/{id}/search` - Search messages

### RAG System
- `POST /api/docs/upload` - Upload documents
- `GET /api/docs` - List documents
- `DELETE /api/docs/{id}` - Delete document

### Research
- `POST /api/research` - Start research task
- `GET /api/research/{run_id}` - Get research status
- `GET /api/research/{run_id}/sources` - Get research sources

### Models & Status
- `GET /api/models` - List available Ollama models
- `GET /api/status` - Check Ollama status
- `GET /health` - Health check endpoint

## Configuration

### Environment Variables

```bash
# Ollama Configuration
OLLAMA_URL=http://127.0.0.1:11434
EMBED_MODEL=nomic-embed-text
DEFAULT_CHAT_MODEL=llama3.1

# Database Paths
CHAT_DB=chat.sqlite3
RAG_DB=rag.sqlite3
WEB_DB=web.sqlite3

# Upload & Security
MAX_UPLOAD_BYTES=10485760
API_KEY=your-secret-key  # Optional API key protection

# Research Models (Optional)
RESEARCH_PLANNER_MODEL=llama3.1
RESEARCH_VERIFIER_MODEL=llama3.1
RESEARCH_SYNTH_MODEL=llama3.1
```

### Search & Scraping Configuration

```bash
# Search Provider Configuration
COGNIHUB_SEARCH_PROVIDER=ddg,searxng  # Comma-separated provider order
SEARXNG_URL=http://localhost:8080  # Local SearxNG instance (for fallback)
WEB_UA=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36

# SSRF Protection
WEB_ALLOWED_HOSTS=example.com,trusted.org
WEB_BLOCKED_HOSTS=malicious.com

# Tool Configuration
ALLOW_SHELL_EXEC=0  # Enable dangerous shell tool (1=enabled)
TOOL_DB=~/.cognihub/data/tool.sqlite3
```

## Development

### Testing

```bash
# Run pytest suite
python -m pytest tests/ -v
```

### Code Quality

```bash
# Type checking
mypy src/cognihub/ --ignore-missing-imports

# Syntax validation
python -m py_compile src/cognihub/app.py src/cognihub/stores/*.py src/cognihub/services/*.py

# Import testing
python -c "import sys; sys.path.insert(0, 'src'); import cognihub.app, cognihub.stores.chatstore, cognihub.stores.ragstore; print('All imports successful')"
```

### Database Operations

```bash
# Check database integrity
sqlite3 chat.sqlite3 "PRAGMA integrity_check;"

# Vacuum databases
sqlite3 chat.sqlite3 "VACUUM;"
sqlite3 rag.sqlite3 "VACUUM;"
```

## Deployment Options



### Manual Linux Deployment

1. **Install services**
   ```bash
   sudo cp systemd/cognihub.service /etc/systemd/system/
   sudo cp systemd/kiwix.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable cognihub kiwix
   ```

2. **Start services**
   ```bash
   sudo systemctl start cognihub kiwix
   ```

### Windows Deployment

See `README_Windows.md` for Windows-specific setup instructions.

## Troubleshooting

### Critical Issues & Solutions

#### 1. Ollama Installation & Setup Issues

**Problem: Ollama not found**
```bash
# Error: bash: ollama: command not found
# Solution: Install Ollama first
sudo pacman -S ollama  # Arch Linux
# Or visit https://ollama.ai/ for other distributions
```

**Problem: Package download fails (404 errors)**
```bash
# Error: Failed retrieving file 'ollama-*.pkg.tar.zst' from mirror
# Solution: Update package databases first
sudo pacman -Syu
sudo pacman -S ollama
```

**Problem: Ollama embeddings API returns 404**
```bash
# Error: Client error '404 Not Found' for url 'http://127.0.0.1:11434/api/embeddings'
# Solution 1: Pull required embedding model
ollama pull nomic-embed-text
# Solution 2: Ensure Ollama is running with embeddings support
ollama serve
```

**Problem: Models return empty responses**
```bash
# Symptom: LLM says "I don't have enough information" or "I don't know" 
# Cause: Search providers blocked or failing silently
# Solution 1: Check search provider status
curl -X POST "https://duckduckgo.com/html/" -d "q=test"
# If you get 302 redirects, DDG is blocking

# Solution 2: Configure search fallback
export COGNIHUB_SEARCH_PROVIDER="ddg,searxng"
# Or use SearxNG only if DDG is consistently blocked
export COGNIHUB_SEARCH_PROVIDER="searxng"
export SEARXNG_URL="https://search.brave.com"

# Solution 3: Run local SearxNG instance (recommended)
docker run -p 8080:8080 -d searxng/searxng
export SEARXNG_URL="http://localhost:8080"

# Or use public SearxNG instances
export SEARXNG_URL="https://searx.be"  # Example public instance
export SEARXNG_URL="https://search.brave.search"  # Another SearxNG-compatible instance

# Solution 4: Check tool execution logs
sqlite3 ~/.cognihub/data/tool.sqlite3 \
  "SELECT tool_name, ok, duration_ms, output_excerpt FROM tool_runs ORDER BY ts DESC LIMIT 5;"
```

**Problem: Search providers consistently fail**
```bash
# Symptom: All web searches return empty or errors
# Solution 1: Test providers directly
python -c "
import asyncio
from src.cognihub.services.web_search import web_search_with_fallback
import httpx
async def test():
    async with httpx.AsyncClient() as http:
        try:
            results, provider = await web_search_with_fallback(http, 'test', 5)
            print(f'Success: {provider}, {len(results)} results')
        except Exception as e:
            print(f'Failed: {e}')
asyncio.run(test())
"

# Solution 2: Update user agent (anti-bot detection)
export WEB_UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Solution 3: Try different search order
export COGNIHUB_SEARCH_PROVIDER="searxng,ddg"
```

#### 2. Python Environment Issues

**Problem: Externally-managed-environment error**
```bash
# Error: This environment is externally managed
# Solution 1: Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Solution 2: Force install (not recommended for production)
pip install -r requirements.txt --break-system-packages
```

**Problem: Commands not found after installation**
```bash
# Error: bash: uvicorn: command not found
# Solution: Add local bin to PATH
export PATH="$HOME/.local/bin:$PATH"
hash -r
command -v uvicorn  # Verify
command -v cognihub-app  # Verify
```

**Problem: Package installation in editable mode fails**
```bash
# Error: externally-managed-environment
# Solution: Use --break-system-packages flag for development
pip install -e . --break-system-packages
```

#### 3. Port & Service Conflicts

**Problem: Port 11434 already in use**
```bash
# Error: listen tcp 127.0.0.1:11434: bind: address already in use
# Solution: Find and kill existing process
sudo lsof -i :11434
sudo kill -9 <PID>
# Or restart Ollama properly
pkill ollama
ollama serve &
```

**Problem: Port 8000 already in use**
```bash
# Solution 1: Kill existing process
sudo lsof -i :8000
sudo kill -9 <PID>

# Solution 2: Use different port
uvicorn src.cognihub.app:app --reload --host 0.0.0.0 --port 8001
```

#### 4. Model Loading & Performance Issues

**Problem: Flash attention warnings**
```bash
# Warning: flash attention enabled but not supported by model
# Solution: This is informational, models will still work
# For better performance, install ollama-vulkan (if supported)
sudo pacman -S ollama-vulkan
OLLAMA_VULKAN=1 ollama serve
```

**Problem: Context size warnings**
```bash
# Warning: requested context size too large for model
# Solution: Reduce context size in chat settings
# Or use model with larger context window
```

**Problem: Slow response times**
```bash
# Symptom: Responses take 10+ seconds
# Solution 1: Check if models are CPU-only (no GPU)
ollama logs | grep "GPU"
# Solution 2: Adjust Ollama for performance
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_NUM_PARALLEL=1
```

#### 5. Dependency & System Issues

**Problem: Missing system dependencies**
```bash
# Error: Various import/dependency errors
# Solution: Install system packages
sudo pacman -S python python-pip sqlite fastapi uvicorn
# For Arch Linux specific packages
sudo pacman -S ollama ollama-vulkan
```

**Problem: Kiwix service fails**
```bash
# Solution: Check if kiwix is installed
sudo pacman -S kiwix-tools
# Or disable Kiwix if not needed
sudo systemctl disable kiwix
sudo systemctl stop kiwix
```

### Common Issues

1. **Ollama Connection Failed**
   - Ensure Ollama is running: `ollama serve &`
   - Check OLLAMA_URL environment variable
   - Verify models are pulled: `ollama list`
   - Test with: `curl http://127.0.0.1:11434/api/tags`

2. **Port Already in Use**
   - Change FastAPI port: `uvicorn src.cognihub.app:app --port 8001`
   - Or set environment: `API_BASE=http://localhost:8001`
   - Find process: `sudo lsof -i :8000`

3. **Database Errors**
   - Check file permissions on SQLite files
   - Run integrity check: `sqlite3 chat.sqlite3 "PRAGMA integrity_check;"`
   - Ensure data directory exists and is writable

4. **High Memory Usage**
   - Adjust cache settings in config.py
   - Monitor with `htop` or `btop`
   - Limit loaded models in Ollama

5. **Embedding Issues**
   - Required: `nomic-embed-text` model (not embeddinggemma)
   - Pull with: `ollama pull nomic-embed-text`
   - Verify: `ollama list | grep embed`

### Debugging Commands

```bash
# Check Ollama status
curl http://127.0.0.1:11434/api/tags
curl http://127.0.0.1:11434/api/version

# Check CogniHub API
curl http://localhost:8000/api/status
curl http://localhost:8000/api/models

# Monitor logs
tail -f ~/.ollama/logs/ollama.log
journalctl -u cognihub -f

# Check system resources
btop  # or htop
free -h
df -h

# Test model manually
ollama run llama3.1 "Hello, test message"
```

### Logs & Monitoring

- **FastAPI logs**: Console output when running uvicorn
- **Ollama logs**: `~/.ollama/logs/ollama.log`
- **Systemd logs**: `journalctl -u cognihub -f`
- **Application logs**: Check console output for errors

### Performance Optimization

```bash
# For CPU-only systems
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_MAX_LOADED_MODELS=1

# For systems with GPU support
sudo pacman -S ollama-vulkan
export OLLAMA_VULKAN=1

# Monitor resource usage
watch -n 1 'free -h && echo "---" && ps aux | grep ollama'
```

## Frequently Encountered Problems

### The "4 Most Common Issues"

1. **404 Not Found for embeddings API**
   - **Cause**: Missing `nomic-embed-text` model
   - **Fix**: `ollama pull nomic-embed-text`

2. **Commands not found after pip install**
   - **Cause**: PATH doesn't include `~/.local/bin`
   - **Fix**: `export PATH="$HOME/.local/bin:$PATH" && hash -r`

3. **Externally-managed-environment error**
   - **Cause**: Modern Python distributions restrict pip installs
   - **Fix**: Use virtual environment or `--break-system-packages`

4. **Ollama connection failed**
   - **Cause**: Ollama not running or wrong port
   - **Fix**: `ollama serve &` or check OLLAMA_URL

### Error Pattern Recognition

| Error Message | Likely Cause | Quick Fix |
|-------------|--------------|-----------|
| `404 Not Found` for `/api/embeddings` | Missing embedding model | `ollama pull nomic-embed-text` |
| `command not found: uvicorn` | PATH issue | `export PATH="$HOME/.local/bin:$PATH"` |
| `externally-managed-environment` | Python protection | Use venv or `--break-system-packages` |
| `address already in use` | Port conflict | `lsof -i :8000` and kill process |
| "I don't have enough information" | Tool-calling failure | Check API status, verify embedding model, test tool endpoints |
| Slow responses (>10s) | CPU-only inference | Install GPU drivers or accept slower speed |

## Contributing

1. Follow code style guidelines in `AGENTS.md`
2. Run tests before committing
3. Update documentation for new features
4. Use type hints and proper error handling

## License

This project is open source. See individual files for license information.
