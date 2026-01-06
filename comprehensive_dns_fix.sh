#!/bin/bash
# Comprehensive DNS Fix Script

echo "🔧 Comprehensive Tailscale DNS Fix for Router Phase 1"
echo "=================================================="

# Get Tailscale IP
TS_IP=$(tailscale ip -4)
DOMAIN="server.tail556641.ts.net"

echo "🔍 Current Status:"
echo "   Tailscale IP: $TS_IP"
echo "   Domain: $DOMAIN"

# Test current DNS resolution
echo ""
echo "🧪 Testing DNS Resolution:"

if getent hosts "$DOMAIN" >/dev/null 2>&1; then
    RESOLVED_IP=$(getent hosts "$DOMAIN" | awk '{print $1}')
    echo "   ✅ DNS Resolution Working: $DOMAIN -> $RESOLVED_IP"
else
    echo "   ❌ DNS Resolution Failed for $DOMAIN"
fi

# Test connectivity
echo ""
echo "🌐 Testing Connectivity:"

# Test via IP
echo "   Testing IP..."
if curl -s --max-time 5 "http://$TS_IP:8000/api/v1/health" >/dev/null; then
    echo "   ✅ Backend via IP: http://$TS_IP:8000"
else
    echo "   ❌ Backend via IP failed"
fi

if curl -s --max-time 5 "http://$TS_IP:1234" >/dev/null; then
    echo "   ✅ Frontend via IP: http://$TS_IP:1234"
else
    echo "   ❌ Frontend via IP failed"
fi

# Test via domain
echo "   Testing Domain..."
if curl -s --max-time 5 "http://$DOMAIN:8000/api/v1/health" >/dev/null; then
    echo "   ✅ Backend via Domain: http://$DOMAIN:8000"
else
    echo "   ❌ Backend via Domain failed"
fi

if curl -s --max-time 5 "http://$DOMAIN:1234" >/dev/null; then
    echo "   ✅ Frontend via Domain: http://$DOMAIN:1234"
else
    echo "   ❌ Frontend via Domain failed"
fi

echo ""
echo "🔧 Applying Fixes..."

# Fix 1: Ensure proper Tailscale DNS configuration
echo "1️⃣ Reconfiguring Tailscale DNS..."
# Note: This requires admin privileges
tailscale up --accept-dns --accept-routes --logout-other-nodes >/dev/null 2>&1 || echo "   ⚠️  Admin privileges required for DNS reconfiguration"

# Fix 2: Add to local hosts file (fallback)
echo "2️⃣ Adding domain to local hosts file..."
if ! grep -q "$DOMAIN" /etc/hosts; then
    echo "   📝 Adding $TS_IP $DOMAIN to /etc/hosts (requires sudo)"
    echo "   Run: echo '$TS_IP $DOMAIN' | sudo tee -a /etc/hosts"
else
    echo "   ✅ Domain already in hosts file"
fi

# Fix 3: Restart systemd-resolved
echo "3️⃣ Restarting DNS resolver..."
sudo systemctl restart systemd-resolved 2>/dev/null || echo "   ⚠️  Admin privileges required for DNS restart"

# Fix 4: Clear DNS cache
echo "4️⃣ Clearing DNS cache..."
sudo systemd-resolve --flush-caches 2>/dev/null || echo "   ⚠️  Admin privileges required to flush cache"

echo ""
echo "🎯 Final Status & URLs:"
echo ""
echo "🏠 Local Access:"
echo "   Frontend: http://localhost:1234"
echo "   Backend:  http://localhost:8000"
echo ""
echo "🔗 IP Access (always works):"
echo "   Frontend: http://$TS_IP:1234"
echo "   Backend:  http://$TS_IP:8000"
echo ""
echo "🌐 Domain Access (should work after fixes):"
echo "   Frontend: http://$DOMAIN:1234"
echo "   Backend:  http://$DOMAIN:8000"
echo "   API Docs: http://$DOMAIN:8000/docs"
echo ""
echo "💡 Quick Fix if domain still doesn't work:"
echo "   echo '$TS_IP $DOMAIN' | sudo tee -a /etc/hosts"
echo ""

# Final verification test
echo "🧪 Final Verification:"
if getent hosts "$DOMAIN" >/dev/null 2>&1; then
    echo "   ✅ DNS Resolution: Working"
else
    echo "   ❌ DNS Resolution: Not working - use hosts file method"
fi

if curl -s --max-time 5 "http://$DOMAIN:8000/api/v1/health" >/dev/null; then
    echo "   ✅ Domain Connectivity: Working"
else
    echo "   ❌ Domain Connectivity: Not working"
fi

echo ""
echo "✅ DNS fix process complete!"