#!/bin/bash
# Tailscale DNS Fix Script

echo "🔧 Fixing Tailscale DNS for server.tail556641.ts.net..."

# Method 1: Restart Tailscale
echo "📡 Restarting Tailscale service..."
sudo systemctl restart tailscaled
sleep 3

# Method 2: Force DNS settings
echo "🌐 Setting up DNS resolution..."
sudo tailscale set --accept-routes --accept-dns=false

# Method 3: Add entry to hosts file
echo "📝 Adding DNS entry to hosts file..."
SERVER_IP=$(tailscale ip -4)
if [ ! -z "$SERVER_IP" ]; then
    echo "$SERVER_IP server.tail556641.ts.net" | sudo tee -a /etc/hosts
    echo "✅ Added $SERVER_IP server.tail556641.ts.net to /etc/hosts"
fi

# Method 4: Test the domain
echo "🧪 Testing domain resolution..."
if nslookup server.tail556641.ts.net >/dev/null 2>&1; then
    echo "✅ DNS resolution working!"
    echo "🎨 Frontend: http://server.tail556641.ts.net:1234"
    echo "🔧 Backend:  http://server.tail556641.ts.net:8000"
else
    echo "❌ DNS still not working, but IP addresses work fine"
    echo "🔗 Use: http://$SERVER_IP:1234 (frontend)"
    echo "🔗 Use: http://$SERVER_IP:8000 (backend)"
fi

echo "✅ DNS fix complete!"