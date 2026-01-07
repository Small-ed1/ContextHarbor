# Troubleshooting and Maintenance Guide

This guide helps diagnose and resolve common issues with Router Phase 1.

## Quick Diagnosis

### Health Check Commands

```bash
# Check service status
sudo systemctl status router-phase1

# Check backend health
curl http://localhost:8000/api/health

# Check Ollama status
curl http://localhost:11434/api/tags

# View recent logs
sudo journalctl -u router-phase1 -n 50

# Check disk space
df -h

# Check memory usage
free -h
```

### Common Symptoms and Solutions

## Issue 1: Application Won't Start

**Symptoms:**
- Service fails to start
- Port 8000 not accessible
- Logs show import errors

**Solutions:**

1. **Check Python Environment**
   ```bash
   cd /path/to/router_phase1
   source venv/bin/activate
   python -c "import fastapi, uvicorn; print('OK')"
   ```

2. **Check Dependencies**
   ```bash
   pip list | grep -E "(fastapi|uvicorn|numpy|faiss)"
   pip install -r requirements.txt
   ```

3. **Check Configuration**
   ```bash
   python -c "import json; json.load(open('config.json'))"
   ```

4. **Check Permissions**
   ```bash
   ls -la data/
   chown -R $USER:$USER data/
   ```

## Issue 2: Ollama Connection Failed

**Symptoms:**
- "Model not available" errors
- Research features not working
- Ollama API errors in logs

**Solutions:**

1. **Verify Ollama is Running**
   ```bash
   sudo systemctl status ollama
   sudo systemctl restart ollama
   ```

2. **Check Model Availability**
   ```bash
   ollama list
   ollama pull llama2:7b  # if missing
   ```

3. **Test API Connection**
   ```bash
   curl http://localhost:11434/api/generate -d '{"model":"llama2:7b","prompt":"test"}'
   ```

4. **Update Configuration**
   ```json
   {
     "ollama_host": "http://localhost:11434"
   }
   ```

## Issue 3: High Memory Usage

**Symptoms:**
- System slowdown
- Out of memory errors
- Application crashes

**Solutions:**

1. **Monitor Memory Usage**
   ```bash
   htop
   free -h
   ```

2. **Adjust Memory Settings**
   ```json
   {
     "memory_threshold": 0.7,
     "max_context_tokens": 2048
   }
   ```

3. **Unload Unused Models**
   ```bash
   ollama stop all-models
   ```

4. **Restart Services**
   ```bash
   sudo systemctl restart router-phase1
   ```

## Issue 4: Vector Store Errors

**Symptoms:**
- Document Q&A not working
- "Index not found" errors
- Search failures

**Solutions:**

1. **Check Vector Store Files**
   ```bash
   ls -la data/vector_store/
   ```

2. **Rebuild Index (CAUTION: Loses data)**
   ```bash
   rm -rf data/vector_store/
   # Restart application to recreate
   ```

3. **Restore from Backup**
   ```bash
   python3 scripts/restore.py --list
   python3 scripts/restore.py backup_name
   ```

4. **Check FAISS Installation**
   ```bash
   python -c "import faiss; print(faiss.__version__)"
   ```

## Issue 5: Database Errors

**Symptoms:**
- Chat history not saving
- Settings not persisting
- SQLite errors in logs

**Solutions:**

1. **Check Database File**
   ```bash
   ls -la router.db
   file router.db
   ```

2. **Database Integrity Check**
   ```bash
   sqlite3 router.db "PRAGMA integrity_check;"
   ```

3. **Backup and Restore**
   ```bash
   cp router.db router.db.backup
   # If corrupted, restore from backup
   ```

4. **Permissions**
   ```bash
   chown $USER:$USER router.db
   chmod 644 router.db
   ```

## Issue 6: Web UI Not Loading

**Symptoms:**
- Blank page
- JavaScript errors in browser console
- 404 errors

**Solutions:**

1. **Check Static Files**
   ```bash
   ls -la frontend/static/
   ```

2. **Clear Browser Cache**
   - Hard refresh: Ctrl+F5

3. **Check CORS Settings**
   ```bash
   curl -H "Origin: http://localhost:8000" http://localhost:8000/api/health
   ```

4. **Rebuild Frontend (if in development)**
   ```bash
   cd frontend
   npm run build
   ```

## Issue 7: Backup Failures

**Symptoms:**
- Backup scripts fail
- Encryption errors
- Permission denied

**Solutions:**

1. **Check Backup Directory**
   ```bash
   ls -la backups/
   mkdir -p backups
   chown $USER:$USER backups
   ```

2. **Test Backup Manually**
   ```bash
   python3 scripts/backup.py --dry-run
   ```

3. **Check GPG for Encryption**
   ```bash
   gpg --version
   # If missing: sudo apt install gnupg
   ```

4. **Service Permissions**
   ```bash
   sudo systemctl edit router-backup.service
   # Add User=your-user
   ```

## Maintenance Tasks

### Daily Maintenance

```bash
# Check service status
sudo systemctl status router-phase1

# Clean old logs
sudo journalctl --vacuum-time=7d

# Backup data
python3 scripts/backup.py
```

### Weekly Maintenance

```bash
# Update system packages
sudo apt update && sudo apt upgrade

# Clean old backups (keep last 5)
python3 scripts/backup.py --cleanup 5

# Check disk usage
df -h
du -sh data/
```

### Monthly Maintenance

```bash
# Update Python packages
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Update Ollama
ollama pull llama2:latest

# Database optimization
sqlite3 router.db "VACUUM;"

# Security audit
pip audit
```

## Performance Optimization

### Slow Response Times

1. **Profile Application**
   ```bash
   python -m cProfile -s time backend/app.py
   ```

2. **Optimize Database**
   ```bash
   sqlite3 router.db "ANALYZE;"
   ```

3. **Cache Static Files**
   ```nginx
   location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
       expires 1y;
       add_header Cache-Control "public, immutable";
   }
   ```

### High CPU Usage

1. **Limit Ollama Threads**
   ```bash
   export OLLAMA_NUM_THREAD=4
   ```

2. **Profile Python Code**
   ```bash
   pip install py-spy
   py-spy top --pid $(pgrep -f "python.*backend")
   ```

## Log Analysis

### Common Log Patterns

**Normal Operation:**
```
INFO: Application started on http://0.0.0.0:8000
INFO: Ollama models loaded: llama2:7b
INFO: Vector store initialized with 1000 vectors
```

**Warnings:**
```
WARNING: High memory usage: 85%
WARNING: Model switching due to temperature
```

**Errors:**
```
ERROR: Failed to connect to Ollama
ERROR: Vector store corrupted
ERROR: Database locked
```

### Log Commands

```bash
# Follow logs
sudo journalctl -u router-phase1 -f

# Search for errors
sudo journalctl -u router-phase1 | grep ERROR

# Logs from last hour
sudo journalctl -u router-phase1 --since "1 hour ago"

# Export logs
sudo journalctl -u router-phase1 > router_logs.txt
```

## Emergency Procedures

### Complete System Reset

**WARNING: This will delete all data**

```bash
# Stop services
sudo systemctl stop router-phase1

# Backup current data (if possible)
cp -r data data.backup

# Reset application
rm -rf data/
rm router.db
git reset --hard HEAD
pip install -r requirements.txt

# Restart
sudo systemctl start router-phase1
```

### Recovery from Backup

```bash
# List available backups
python3 scripts/restore.py --list

# Restore specific backup
python3 scripts/restore.py backup_20241201_020000

# Verify restoration
curl http://localhost:8000/api/health
```

## Support and Resources

### Getting Help

1. Check this guide first
2. Review GitHub issues
3. Check Ollama documentation
4. Search FastAPI/FAISS documentation

### Useful Commands

```bash
# System info
uname -a
python --version
pip list

# Process info
ps aux | grep -E "(python|ollama)"
top -p $(pgrep -f "python.*backend")

# Network
netstat -tlnp | grep :8000
curl -I http://localhost:8000
```

### Configuration Backup

Always backup your configuration:

```bash
cp config.json config.json.backup
cp .env .env.backup
cp -r config/ config.backup/
```