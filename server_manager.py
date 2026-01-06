#!/usr/bin/env python3
"""
Server Management utility for Router Phase 1
Ensures proper server restarts after code changes
"""

import asyncio
import logging
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ServerManager:
    """Manages backend and frontend servers with proper restarts"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.processes: Dict[str, subprocess.Popen] = {}
        self.running = True
        
    async def start_servers(self):
        """Start all necessary servers"""
        logger.info("🚀 Starting Router Phase 1 servers...")
        
        # Start backend server
        await self.start_backend()
        
        # Start frontend server
        await self.start_frontend()
        
        # Check Ollama is running
        await self.check_ollama()
        
        logger.info("✅ All servers started successfully")
        
    async def start_backend(self):
        """Start FastAPI backend server"""
        logger.info("🔧 Starting FastAPI backend server...")
        
        # Kill existing backend process
        await self.kill_existing_process("uvicorn")
        
        # Start new backend process
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "backend.app:app",
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ]
        
        try:
            process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes["backend"] = process
            logger.info("✅ Backend server started on http://0.0.0.0:8000")
            
            # Wait a moment for startup
            await asyncio.sleep(2)
            
            # Verify it's running
            if process.poll() is None:
                logger.info("✅ Backend server is running")
            else:
                logger.error("❌ Backend server failed to start")
                stdout, stderr = process.communicate()
                logger.error(f"Stdout: {stdout}")
                logger.error(f"Stderr: {stderr}")
                
        except Exception as e:
            logger.error(f"❌ Failed to start backend: {e}")
            
    async def start_frontend(self):
        """Start frontend development server"""
        logger.info("🎨 Starting frontend development server...")
        
        # Kill existing frontend process
        await self.kill_existing_process("parcel")
        
        # Install dependencies if needed
        frontend_dir = self.project_root / "frontend"
        node_modules = frontend_dir / "node_modules"
        
        if not node_modules.exists():
            logger.info("📦 Installing frontend dependencies...")
            npm_install = subprocess.run(
                ["npm", "install"],
                cwd=frontend_dir,
                capture_output=True,
                text=True
            )
            if npm_install.returncode != 0:
                logger.error(f"❌ npm install failed: {npm_install.stderr}")
                return
            logger.info("✅ Dependencies installed")
        
        # Start frontend development server
        cmd = ["npm", "start"]
        
        try:
            process = subprocess.Popen(
                cmd,
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes["frontend"] = process
            logger.info("✅ Frontend server starting...")
            
            # Wait for parcel to start
            await asyncio.sleep(5)
            
            if process.poll() is None:
                logger.info("✅ Frontend server is running")
            else:
                logger.error("❌ Frontend server failed to start")
                stdout, stderr = process.communicate()
                logger.error(f"Stdout: {stdout}")
                logger.error(f"Stderr: {stderr}")
                
        except Exception as e:
            logger.error(f"❌ Failed to start frontend: {e}")
            
    async def check_ollama(self):
        """Check if Ollama is running"""
        logger.info("🤖 Checking Ollama service...")
        
        try:
            # Test Ollama API
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:11434/api/tags", timeout=5) as response:
                    if response.status == 200:
                        models = await response.json()
                        model_count = len(models.get("models", []))
                        logger.info(f"✅ Ollama is running with {model_count} models")
                    else:
                        logger.warning(f"⚠️  Ollama responded with status {response.status}")
        except Exception as e:
            logger.error(f"❌ Ollama is not accessible: {e}")
            logger.info("💡 Make sure Ollama is installed and running: ollama serve")
            
    async def restart_backend(self):
        """Restart backend server"""
        logger.info("🔄 Restarting backend server...")
        await self.start_backend()
        
    async def restart_frontend(self):
        """Restart frontend server"""
        logger.info("🔄 Restarting frontend server...")
        await self.start_frontend()
        
    async def kill_existing_process(self, name: str):
        """Kill existing processes by name"""
        try:
            result = subprocess.run(
                ["pkill", "-f", name],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                logger.info(f"🔪 Killed existing {name} processes")
                await asyncio.sleep(1)
        except Exception as e:
            logger.debug(f"No existing {name} processes to kill: {e}")
            
    async def stop_all(self):
        """Stop all managed servers"""
        logger.info("🛑 Stopping all servers...")
        self.running = False
        
        for name, process in self.processes.items():
            try:
                process.terminate()
                await asyncio.sleep(1)
                if process.poll() is None:
                    process.kill()
                logger.info(f"✅ Stopped {name} server")
            except Exception as e:
                logger.error(f"❌ Error stopping {name}: {e}")
                
    async def monitor_servers(self):
        """Monitor servers and restart if needed"""
        while self.running:
            try:
                # Check backend
                if "backend" in self.processes:
                    if self.processes["backend"].poll() is not None:
                        logger.warning("⚠️  Backend server died, restarting...")
                        await self.start_backend()
                        
                # Check frontend
                if "frontend" in self.processes:
                    if self.processes["frontend"].poll() is not None:
                        logger.warning("⚠️  Frontend server died, restarting...")
                        await self.start_frontend()
                        
            except Exception as e:
                logger.error(f"❌ Error monitoring servers: {e}")
                
            await asyncio.sleep(10)
            
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            self.running = False
            asyncio.create_task(self.stop_all())
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)


async def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python server_manager.py <command>")
        print("Commands:")
        print("  start     - Start all servers")
        print("  restart   - Restart all servers") 
        print("  stop      - Stop all servers")
        print("  status    - Check server status")
        print("  monitor   - Start and monitor servers")
        sys.exit(1)
        
    command = sys.argv[1]
    project_root = Path(__file__).parent
    manager = ServerManager(project_root)
    manager.setup_signal_handlers()
    
    try:
        if command == "start":
            await manager.start_servers()
            print("✅ Servers started. Run 'python server_manager.py monitor' to keep them running.")
            
        elif command == "restart":
            await manager.stop_all()
            await asyncio.sleep(2)
            await manager.start_servers()
            print("✅ Servers restarted. Run 'python server_manager.py monitor' to keep them running.")
            
        elif command == "stop":
            await manager.stop_all()
            print("✅ All servers stopped.")
            
        elif command == "status":
            print("🔍 Checking server status...")
            # Check Ollama
            try:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get("http://localhost:11434/api/tags", timeout=2) as response:
                        if response.status == 200:
                            models = await response.json()
                            print(f"✅ Ollama: Running ({len(models.get('models', []))} models)")
                        else:
                            print(f"⚠️  Ollama: HTTP {response.status}")
            except:
                print("❌ Ollama: Not running")
                
            # Check Backend
            try:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get("http://localhost:8000/api/v1/health", timeout=2) as response:
                        if response.status == 200:
                            print("✅ Backend: Running")
                        else:
                            print(f"⚠️  Backend: HTTP {response.status}")
            except:
                print("❌ Backend: Not running")
                
            # Check Frontend
            try:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get("http://localhost:1234", timeout=2) as response:
                        if response.status == 200:
                            print("✅ Frontend: Running")
                        else:
                            print(f"⚠️  Frontend: HTTP {response.status}")
            except:
                print("❌ Frontend: Not running")
                
        elif command == "monitor":
            await manager.start_servers()
            print("👀 Monitoring servers... Press Ctrl+C to stop.")
            await manager.monitor_servers()
            
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        await manager.stop_all()


if __name__ == "__main__":
    asyncio.run(main())