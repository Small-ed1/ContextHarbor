#!/bin/bash
# Post-edit server restart script for Router Phase 1
# This script should be run after making code changes to ensure servers are restarted

PROJECT_ROOT="$(dirname "$0")"
cd "$PROJECT_ROOT"

echo "Post-edit server restart for Router Phase 1..."

# Function to check if process is running and kill it
restart_service() {
    local service_name=$1
    local port=$2
    local start_cmd=$3
    
    echo "Restarting $service_name..."
    
    # Find and kill existing process
    if lsof -i:$port >/dev/null 2>&1; then
        echo "  Stopping existing $service_name (port $port)..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
    # Start the service
    echo "  Starting $service_name..."
    cd "$PROJECT_ROOT"
    eval "$start_cmd" &
    
    # Wait for service to start
    local max_wait=10
    local wait_time=0
    while [ $wait_time -lt $max_wait ]; do
        if curl -s "http://localhost:$port" >/dev/null 2>&1 || \
           curl -s "http://localhost:$port/api/v1/health" >/dev/null 2>&1; then
            echo "  $service_name is running"
            return 0
        fi
        sleep 1
        wait_time=$((wait_time + 1))
        echo "    Waiting for $service_name to start... ($wait_time/$max_wait)"
    done
    
    echo "  $service_name may not have started properly"
    return 1
}

# Restart services based on what was likely changed
if [ "$1" = "backend" ] || [ "$1" = "all" ]; then
    restart_service "Backend" 8000 "uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload"
fi

if [ "$1" = "frontend" ] || [ "$1" = "all" ]; then
    restart_service "Frontend" 1234 "cd frontend && npm start"
fi

# Check Ollama status
echo "Checking Ollama..."
if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "Ollama is running"
else
    echo "Ollama is not accessible"
    echo "Make sure Ollama is running: ollama serve"
fi

echo ""
echo "Final Status:"
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:1234"
echo "  Ollama:   http://localhost:11434"
echo ""
echo "Post-edit restart complete!"

# Display quick test commands
echo ""
echo "Quick test commands:"
echo "  curl http://localhost:8000/api/v1/health"
echo "  curl http://localhost:8000/api/models"
echo "  curl -I http://localhost:1234"