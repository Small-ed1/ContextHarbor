#!/bin/bash

# Script to set OLLAMA_NUM_THREAD=9 for Ollama service (80% of 12 threads)

set -e

echo "Creating Ollama service drop-in to limit threads to 9..."

sudo mkdir -p /etc/systemd/system/ollama.service.d

sudo tee /etc/systemd/system/ollama.service.d/override.conf > /dev/null << 'EOF'
[Service]
Environment=OLLAMA_NUM_THREAD=9
EOF

echo "Reloading systemd and restarting Ollama..."

sudo systemctl daemon-reload
sudo systemctl restart ollama

echo "Done! Ollama is now limited to 9 threads."
echo "Verify with: systemctl show ollama | grep OLLAMA_NUM_THREAD"