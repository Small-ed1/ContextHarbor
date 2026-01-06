#!/usr/bin/env python3
"""
Network Access Helper for Router Phase 1
Provides multiple ways to access the application when Tailscale DNS is not working
"""

import subprocess
import sys
from pathlib import Path

def get_local_ip():
    """Get the primary local IP address"""
    try:
        result = subprocess.run(
            ["ip", "route", "get", "1.1.1.1"], 
            capture_output=True, 
            text=True
        )
        for line in result.stdout.split('\n'):
            if "src" in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "src" and i + 1 < len(parts):
                        return parts[i + 1]
    except:
        pass
    
    return "127.0.0.1"  # fallback

def get_tailscale_ip():
    """Get Tailscale IP address"""
    try:
        result = subprocess.run(
            ["tailscale", "ip", "-4"], 
            capture_output=True, 
            text=True
        )
        return result.stdout.strip()
    except:
        return None

def main():
    print("🌐 Router Phase 1 - Network Access Options")
    print("=" * 50)
    
    # Get network information
    local_ip = get_local_ip()
    tailscale_ip = get_tailscale_ip()
    
    print(f"🏠 Local IP: {local_ip}")
    if tailscale_ip:
        print(f"🔗 Tailscale IP: {tailscale_ip}")
    
    print("\n📱 Access URLs:")
    print("\n1. Local Access (on this machine):")
    print(f"   🎨 Frontend: http://localhost:1234")
    print(f"   🔧 Backend:  http://localhost:8000")
    print(f"   📚 API Docs: http://localhost:8000/docs")
    
    print("\n2. Local Network Access (other devices on same network):")
    print(f"   🎨 Frontend: http://{local_ip}:1234")
    print(f"   🔧 Backend:  http://{local_ip}:8000")
    
    if tailscale_ip:
        print("\n3. Tailscale Network Access (other Tailscale devices):")
        print(f"   🎨 Frontend: http://{tailscale_ip}:1234")
        print(f"   🔧 Backend:  http://{tailscale_ip}:8000")
    
    print("\n🔧 Troubleshooting:")
    print("• If Tailscale DNS doesn't work, use the IP addresses above")
    print("• Make sure ports 8000 and 1234 are open in firewall")
    print("• For HTTPS, you can use Tailscale certificates if you have admin access")
    print("• Check if services are running with: python server_manager.py status")
    
    print("\n📝 Quick Test Commands:")
    print(f"curl http://localhost:8000/api/v1/health")
    print(f"curl http://localhost:8000/api/models")
    print(f"curl -I http://localhost:1234")
    
    if tailscale_ip:
        print(f"\n🔗 Share these URLs with other Tailscale devices:")
        print(f"   Frontend: http://{tailscale_ip}:1234")
        print(f"   Backend API: http://{tailscale_ip}:8000")

if __name__ == "__main__":
    main()