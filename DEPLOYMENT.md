# Router Phase 1 Deployment Guide

## Overview
Router Phase 1 is a web-based Tailnet LLM dashboard with advanced research capabilities. This guide covers deployment options and setup.

## Prerequisites
- Python 3.13+
- Node.js 18+
- Docker (optional)
- Ollama for local LLM support

## Quick Start with Docker

### Using Docker Compose
```bash
# Clone the repository
git clone <repository-url>
cd router-phase1

# Build and start services
docker-compose up --build
```

This starts:
- Backend API on port 8000
- Frontend on port 3000
- Ollama on port 11434

### Manual Docker Build
```bash
# Build backend
docker build -t router-phase1-backend .

# Run backend
docker run -p 8000:8000 router-phase1-backend

# Build frontend
cd frontend
docker build -t router-phase1-frontend .
docker run -p 3000:3000 router-phase1-frontend
```

## Manual Installation

### Backend Setup
```bash
# Install dependencies
pip install -r backend/requirements.txt

# Set environment variables (optional)
export OLLAMA_HOST=http://localhost:11434
export PYTHONPATH=/path/to/backend

# Start server
uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run build
# Serve static files from backend/static
```

### Ollama Setup
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama
ollama serve

# Pull models
ollama pull llama3.2:1b
```

## Production Deployment

### Systemd Service
```bash
# Copy service file
sudo cp router-phase1.service /etc/systemd/system/

# Enable and start
sudo systemctl enable router-phase1
sudo systemctl start router-phase1

# Check status
sudo systemctl status router-phase1
```

### Reverse Proxy (nginx)
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/backend/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### SSL with Let's Encrypt
```bash
# Install certbot
sudo pacman -S certbot certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com
```

## Configuration

### Environment Variables
- `OLLAMA_HOST`: Ollama server URL (default: http://127.0.0.1:11434)
- `OLLAMA_MODEL`: Default model (default: llama3.2:1b)
- `PYTHONPATH`: Backend path

### Settings
Access `/settings` in the web UI to configure:
- Theme preferences
- Model selection
- Research depth
- API endpoints

## Backup and Recovery

### Data Backup
```bash
# Backup research sessions
cp -r ~/.router-phase1/sessions /backup/location

# Backup vector stores (if using FAISS)
cp -r ~/.router-phase1/vectors /backup/location
```

### Restore
```bash
# Restore sessions
cp -r /backup/location/sessions ~/.router-phase1/
```

## Monitoring

### Health Checks
```bash
# Backend health
curl http://localhost:8000/api/v1/health

# Ollama status
curl http://localhost:11434/api/tags
```

### Logs
```bash
# Systemd logs
journalctl -u router-phase1 -f

# Application logs
tail -f /tmp/router_servers.log
```

## Troubleshooting

### Common Issues

1. **Ollama connection failed**
   - Ensure Ollama is running: `ollama serve`
   - Check OLLAMA_HOST environment variable

2. **Static files not loading**
   - Verify frontend build completed
   - Check static file serving configuration

3. **Research tasks failing**
   - Verify model availability
   - Check memory usage
   - Review research session logs

### Performance Tuning
- Increase `OLLAMA_NUM_PARALLEL` for concurrent requests
- Adjust `OLLAMA_MAX_LOADED_MODELS` for memory management
- Use `--workers` with uvicorn for multi-core systems

## Security Considerations
- Run behind reverse proxy with SSL
- Use strong authentication for sensitive features
- Regularly update dependencies
- Monitor resource usage
- Implement rate limiting for API endpoints

## Support
For issues and questions:
- Check logs in `/tmp/router_servers.log`
- Review API documentation at `/docs`
- Test endpoints with the provided curl commands