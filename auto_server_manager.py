#!/usr/bin/env python3
"""
Automatic Server Manager for Router Phase 1
Ensures servers are always running and auto-start on boot
"""

import asyncio
import json
import logging
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional
import socket

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/router_servers.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AutoServerManager:
    """Manages servers with automatic restart and boot-time startup"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.processes: Dict[str, subprocess.Popen] = {}
        self.running = True
        self.config_file = project_root / "server_config.json"
        self.pid_file = project_root / ".server_manager.pid"
        self.health_check_interval = 30  # seconds
        
    def load_config(self) -> Dict:
        """Load server configuration"""
        default_config = {
            "services": {
                "ollama": {
                    "check_command": "curl -s http://localhost:11434/api/tags > /dev/null 2>&1",
                    "start_command": "ollama serve",
                    "port": 11434,
                    "name": "Ollama",
                    "autostart": True
                },
                "backend": {
                    "check_command": "curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1",
                    "start_command": "uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload",
                    "port": 8000,
                    "name": "Backend FastAPI",
                    "autostart": True
                },
                "frontend": {
                    "check_command": "curl -s -I http://localhost:1234 > /dev/null 2>&1",
                    "start_command": "cd frontend && npm start",
                    "port": 1234,
                    "name": "Frontend Dev Server",
                    "autostart": True
                }
            },
            "monitoring": {
                "enabled": True,
                "health_check_interval": 30,
                "restart_on_failure": True,
                "max_restart_attempts": 3
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                # Merge with defaults
                for key in default_config:
                    if key not in loaded_config:
                        loaded_config[key] = default_config[key]
                return loaded_config
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                return default_config
        else:
            # Save default config
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def is_port_in_use(self, port: int) -> bool:
        """Check if port is in use"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(('localhost', port)) == 0
        except:
            return False
    
    def kill_existing_processes(self, port: int, service_name: str):
        """Kill existing processes using a port"""
        try:
            # Find processes using port
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        try:
                            subprocess.run(["kill", "-9", pid], check=False)
                            logger.info(f"Killed process {pid} for {service_name}")
                        except:
                            pass
                time.sleep(1)
        except FileNotFoundError:
            # lsof not available, use pkill as fallback
            if service_name.lower() == "ollama":
                subprocess.run(["pkill", "-f", "ollama"], check=False)
            elif service_name.lower() == "backend":
                subprocess.run(["pkill", "-f", "uvicorn"], check=False)
            elif service_name.lower() == "frontend":
                subprocess.run(["pkill", "-f", "parcel"], check=False)
    
    def is_service_healthy(self, service_config: Dict) -> bool:
        """Check if a service is healthy"""
        try:
            check_command = service_config["check_command"]
            result = subprocess.run(
                check_command.split(),
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            logger.debug(f"Health check failed for {service_config['name']}: {e}")
            return False
    
    def start_service(self, service_name: str, service_config: Dict) -> bool:
        """Start a service"""
        try:
            logger.info(f"Starting {service_config['name']}...")
            
            # Kill existing processes
            self.kill_existing_processes(service_config["port"], service_name)
            
            # Start service
            start_command = service_config["start_command"]
            process = subprocess.Popen(
                start_command,
                shell=True,
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes[service_name] = process
            
            # Wait for service to be healthy
            max_wait = 30
            wait_time = 0
            while wait_time < max_wait:
                if self.is_service_healthy(service_config):
                    logger.info(f"✅ {service_config['name']} is healthy and running")
                    return True
                if process.poll() is not None:
                    logger.error(f"❌ {service_config['name']} failed to start")
                    stdout, stderr = process.communicate()
                    logger.error(f"Stdout: {stdout}")
                    logger.error(f"Stderr: {stderr}")
                    return False
                time.sleep(2)
                wait_time += 2
                logger.debug(f"Waiting for {service_config['name']} to be healthy... ({wait_time}/{max_wait})")
            
            logger.warning(f"⚠️  {service_config['name']} started but health check timed out")
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to start {service_config['name']}: {e}")
            return False
    
    def start_all_services(self) -> bool:
        """Start all configured services"""
        config = self.load_config()
        services = config["services"]
        success_count = 0
        total_count = 0
        
        for service_name, service_config in services.items():
            if service_config.get("autostart", True):
                total_count += 1
                if self.start_service(service_name, service_config):
                    success_count += 1
            else:
                logger.info(f"⏭️  Skipping {service_config['name']} (autostart disabled)")
        
        logger.info(f"📊 Services started: {success_count}/{total_count}")
        return success_count == total_count
    
    async def monitor_services(self):
        """Continuously monitor and restart services if needed"""
        config = self.load_config()
        
        if not config["monitoring"]["enabled"]:
            logger.info("🔍 Monitoring disabled, exiting monitor loop")
            return
        
        interval = config["monitoring"]["health_check_interval"]
        max_attempts = config["monitoring"]["max_restart_attempts"]
        
        restart_attempts = {}
        
        logger.info(f"👀 Starting service monitoring (interval: {interval}s)")
        
        while self.running:
            try:
                services = config["services"]
                
                for service_name, service_config in services.items():
                    if not service_config.get("autostart", True):
                        continue
                    
                    # Check if service is healthy
                    if not self.is_service_healthy(service_config):
                        logger.warning(f"⚠️  {service_config['name']} is unhealthy")
                        
                        # Check restart attempts
                        attempts = restart_attempts.get(service_name, 0)
                        if attempts >= max_attempts:
                            logger.error(f"❌ Max restart attempts ({max_attempts}) reached for {service_config['name']}")
                            continue
                        
                        # Restart service
                        logger.info(f"🔄 Restarting {service_config['name']} (attempt {attempts + 1}/{max_attempts})")
                        if self.start_service(service_name, service_config):
                            restart_attempts[service_name] = 0  # Reset on success
                        else:
                            restart_attempts[service_name] = attempts + 1
                
                # Check if processes are still running
                for service_name, process in list(self.processes.items()):
                    if process.poll() is not None:
                        logger.warning(f"⚠️  Process for {service_name} died, restarting...")
                        service_config = config["services"][service_name]
                        self.start_service(service_name, service_config)
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def stop_all_services(self):
        """Stop all managed services"""
        logger.info("🛑 Stopping all services...")
        self.running = False
        
        for service_name, process in self.processes.items():
            try:
                if process.poll() is None:
                    process.terminate()
                    await asyncio.sleep(2)
                    if process.poll() is None:
                        process.kill()
                    logger.info(f"✅ Stopped {service_name}")
            except Exception as e:
                logger.error(f"❌ Error stopping {service_name}: {e}")
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            self.running = False
            asyncio.create_task(self.stop_all_services())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def write_pid_file(self):
        """Write PID file for process management"""
        try:
            with open(self.pid_file, 'w') as f:
                f.write(str(os.getpid()))
        except Exception as e:
            logger.error(f"Error writing PID file: {e}")
    
    def remove_pid_file(self):
        """Remove PID file"""
        try:
            if self.pid_file.exists():
                self.pid_file.unlink()
        except Exception as e:
            logger.error(f"Error removing PID file: {e}")


def run_main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python auto_server_manager.py <command>")
        print("Commands:")
        print("  start     - Start all services")
        print("  monitor   - Start and continuously monitor services") 
        print("  stop      - Stop all services")
        print("  status    - Check service status")
        print("  install   - Install auto-start on boot")
        sys.exit(1)
    
    command = sys.argv[1]
    project_root = Path(__file__).parent
    manager = AutoServerManager(project_root)
    
    try:
        if command == "start":
            success = manager.start_all_services()
            if success:
                print("✅ All services started successfully")
                sys.exit(0)
            else:
                print("❌ Some services failed to start")
                sys.exit(1)
                
        elif command == "monitor":
            manager.setup_signal_handlers()
            manager.write_pid_file()
            
            # Start services first
            if manager.start_all_services():
                print("👀 Services started, beginning continuous monitoring...")
                print("📝 Logs: /tmp/router_servers.log")
                print("Press Ctrl+C to stop")
                asyncio.run(manager.monitor_services())
            else:
                print("❌ Failed to start services, exiting")
                
        elif command == "stop":
            asyncio.run(manager.stop_all_services())
            print("✅ All services stopped")
            
        elif command == "status":
            print("🔍 Checking service status...")
            config = manager.load_config()
            services = config["services"]
            
            for service_name, service_config in services.items():
                if manager.is_service_healthy(service_config):
                    print(f"✅ {service_config['name']}: Running")
                else:
                    print(f"❌ {service_config['name']}: Not running")
                    
        elif command == "install":
            install_autostart()
            
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        if command in ["monitor", "stop"]:
            asyncio.run(manager.stop_all_services())
            manager.remove_pid_file()


def install_autostart():
    """Install auto-start configuration"""
    print("🔧 Installing auto-start configuration...")
    
    project_root = Path(__file__).parent.absolute()
    manager_script = project_root / "auto_server_manager.py"
    
    # Create systemd service
    service_content = f"""[Unit]
Description=Router Phase 1 Auto Server Manager
After=network.target

[Service]
Type=simple
User={os.getenv('USER')}
WorkingDirectory={project_root}
ExecStart=/usr/bin/python3 {manager_script} monitor
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
    
    service_file = Path("/tmp/router-auto-manager.service")
    with open(service_file, 'w') as f:
        f.write(service_content)
    
    print(f"📄 Service file created: {service_file}")
    print("🔐 To install, run:")
    print(f"   sudo cp {service_file} /etc/systemd/system/")
    print("   sudo systemctl daemon-reload")
    print("   sudo systemctl enable router-auto-manager.service")
    print("   sudo systemctl start router-auto-manager.service")
    print("")
    print("📋 To check status:")
    print("   sudo systemctl status router-auto-manager")
    print("   sudo journalctl -u router-auto-manager -f")


if __name__ == "__main__":
    run_main()