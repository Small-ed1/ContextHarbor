# Environment Setup and Configuration

This document describes the environment requirements and configuration options for Router Phase 1.

## System Requirements

### Minimum Requirements
- **OS**: Linux (Ubuntu 20.04+, CentOS 7+, or equivalent)
- **CPU**: 4-core processor (x86_64 or ARM64)
- **RAM**: 8GB
- **Storage**: 20GB free space
- **Network**: Stable internet connection for model downloads

### Recommended Requirements
- **OS**: Ubuntu 22.04 LTS
- **CPU**: 8-core processor with AVX2 support
- **RAM**: 16GB or more
- **Storage**: 50GB SSD (NVMe preferred)
- **GPU**: NVIDIA GPU with 8GB+ VRAM (optional, for accelerated inference)

## Software Dependencies

### Required Packages

#### Python Environment
```bash
# Python version
python3 --version  # 3.8 or later required

# Virtual environment setup
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt
```

#### System Packages (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    wget \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev
```

#### Ollama Setup
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start service
sudo systemctl start ollama
sudo systemctl enable ollama

# Verify installation
ollama --version
ollama list
```

## Configuration Files

### Main Configuration (config.json)

```json
{
  "host": "0.0.0.0",
  "port": 8000,
  "ollama_host": "http://localhost:11434",
  "default_model": "llama2:7b",
  "max_context_tokens": 4096,
  "temperature": 0.7,
  "auto_model_switching": true,
  "memory_threshold": 0.8,
  "log_level": "INFO",
  "data_directory": "data",
  "backup_directory": "backups"
}
```

### Environment Variables

Create a `.env` file in the project root:

```bash
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_TIMEOUT=300

# Application Settings
ROUTER_HOST=0.0.0.0
ROUTER_PORT=8000
ROUTER_DEBUG=false

# Security
SECRET_KEY=your-secret-key-here
OWNER_PASSWORD=your-owner-password

# Database
DATABASE_URL=sqlite:///router.db

# Vector Store
VECTOR_STORE_DIMENSION=768
VECTOR_STORE_INDEX_TYPE=IndexFlatIP

# Backup
BACKUP_ENCRYPTION_PASSWORD=your-encryption-password
BACKUP_RETENTION_DAYS=30
```

## Directory Structure

After setup, your directory should look like:

```
router_phase1/
├── config/
│   ├── router-phase1.service
│   ├── router-phase1-backend.service
│   └── router-backup.*
├── data/
│   ├── vector_store/
│   │   ├── vector_index.faiss
│   │   └── metadata.json
│   ├── documents/
│   ├── research_sessions/
│   └── router.db
├── backups/
├── docs/
├── frontend/
├── backend/
├── scripts/
├── utils/
├── requirements.txt
├── config.json
└── .env
```

## Model Configuration

### Recommended Models

For general use:
```bash
ollama pull llama2:7b
ollama pull mistral:7b
```

For coding tasks:
```bash
ollama pull codellama:7b
ollama pull deepseek-coder:6.7b
```

For research:
```bash
ollama pull llama2:13b
ollama pull mixtral:8x7b
```

### Model Settings

Configure model parameters in the web UI or via API:

- **Temperature**: 0.1-0.3 for factual tasks, 0.7-0.9 for creative
- **Context Window**: 2048-4096 tokens (balance with RAM)
- **Threads**: Match your CPU cores
- **GPU Layers**: Use GPU if available

## Network Configuration

### Firewall Settings

```bash
# Allow HTTP
sudo ufw allow 8000

# Allow Ollama API (if remote)
sudo ufw allow 11434

# Enable firewall
sudo ufw enable
```

### Reverse Proxy (Optional)

For production with Nginx:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### SSL Configuration

```bash
# Using certbot for Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Monitoring and Maintenance

### Log Configuration

Logs are stored in systemd journal:

```bash
# View application logs
sudo journalctl -u router-phase1 -f

# View backup logs
sudo journalctl -u router-backup -f
```

### Health Checks

Endpoints for monitoring:

- `GET /api/health` - Overall health status
- `GET /api/health/vector-store` - Vector store status
- `GET /api/health/models` - Model availability

### Automated Maintenance

```bash
# Clean old backups (keeps last 10)
python3 scripts/backup.py --cleanup 10

# Update dependencies
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Restart services
sudo systemctl restart router-phase1
```

## Performance Tuning

### Memory Optimization

- Set `memory_threshold` in config.json to 0.8
- Use smaller models for limited RAM
- Enable model unloading in Ollama

### CPU Optimization

- Set Ollama threads to match CPU cores
- Use `num_thread` parameter in model configs

### Storage Optimization

- Use SSD storage for data directory
- Enable compression for backups
- Regular cleanup of old logs

## Troubleshooting

For common issues, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Security Considerations

- Change default passwords
- Use strong SECRET_KEY
- Enable SSL in production
- Restrict network access if possible
- Regular security updates