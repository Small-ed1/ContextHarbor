#!/bin/bash
# Tailscale DNS Priority Fix Script

echo "🔧 Fixing Tailscale DNS Priority for domain names to work..."

echo "📋 Current DNS configuration:"
resolvectl status | grep -A 10 "Link 3 (tailscale0)"

echo ""
echo "🔄 Resetting and reconfiguring DNS..."

# Step 1: Reset DNS settings
echo "1️⃣ Resetting Tailscale network interface..."
sudo ip link set tailscale0 down
sleep 2
sudo ip link set tailscale0 up
sleep 2

# Step 2: Reconfigure Tailscale with DNS priority
echo "2️⃣ Reconfiguring Tailscale with DNS priority..."
sudo tailscale up --accept-dns --accept-routes

# Step 3: Flush DNS cache
echo "3️⃣ Flushing DNS cache..."
sudo systemd-resolve --flush-caches

# Step 4: Test domain resolution
echo "4️⃣ Testing domain resolution..."
sleep 3

if ping -c 1 server.tail556641.ts.net >/dev/null 2>&1; then
    echo "✅ Domain resolution working!"
    echo "🎨 Frontend: http://server.tail556641.ts.net:1234"
    echo "🔧 Backend:  http://server.tail556641.ts.net:8000"
    echo "📚 API Docs: http://server.tail556641.ts.net:8000/docs"
else
    echo "❌ DNS still not working properly"
    
    # Fallback: Add to hosts file
    echo "🔧 Adding fallback entry to hosts file..."
    SERVER_IP=$(tailscale ip -4)
    if [ ! -z "$SERVER_IP" ]; then
        # Remove existing entry if present
        sudo sed -i '/server\.tail556641\.ts\.net/d' /etc/hosts
        # Add new entry
        echo "$SERVER_IP server.tail556641.ts.net" | sudo tee -a /etc/hosts
        echo "✅ Added $SERVER_IP server.tail556641.ts.net to /etc/hosts"
        
        echo "🎨 Frontend: http://server.tail556641.ts.net:1234"
        echo "🔧 Backend:  http://server.tail556641.ts.net:8000"
    fi
fi

echo ""
echo "🧪 Final verification:"
echo "curl http://server.tail556641.ts.net:8000/api/v1/health"
echo "curl http://server.tail556641.ts.net:1234"

echo ""
echo "✅ DNS fix complete!"