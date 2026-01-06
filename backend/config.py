import os
import json
import psutil
import httpx
from pathlib import Path
from typing import Dict, Any, List, Optional

class AutoConfig:
    def __init__(self):
        self.ollama_host = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
        self.config_path = Path("config.json")

    async def detect_ollama_models(self) -> List[str]:
        """Detect available Ollama models"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.ollama_host}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            print(f"Failed to detect Ollama models: {e}")
        return []

    def profile_hardware(self) -> Dict[str, Any]:
        """Profile system hardware"""
        return {
            "cpu_count": psutil.cpu_count(),
            "cpu_count_logical": psutil.cpu_count(logical=True),
            "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "memory_available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
            "disk_total_gb": round(psutil.disk_usage('/').total / (1024**3), 2),
            "disk_free_gb": round(psutil.disk_usage('/').free / (1024**3), 2),
        }

    def get_recommended_config(self, hardware: Dict[str, Any], models: List[str]) -> Dict[str, Any]:
        """Generate recommended configuration based on hardware and models"""
        memory_gb = hardware["memory_total_gb"]
        config = {
            "ollama_host": self.ollama_host,
            "default_model": "llama3.2:latest" if "llama3.2:latest" in models else (models[0] if models else None),
            "embedding_model": "nomic-embed-text" if "nomic-embed-text" in models else None,
            "max_memory_usage_gb": min(memory_gb * 0.8, 12.0),  # Use 80% of RAM, max 12GB
            "chunk_size": 1000 if memory_gb > 8 else 500,
            "max_workers": min(hardware["cpu_count"] // 2, 4),
            "enable_gpu": False,  # Add GPU detection later
            "research_time_limit_hours": 24,
            "rag_maintenance_interval_days": 7,
        }
        return config

    async def run_first_time_setup(self) -> Dict[str, Any]:
        """Run first-time setup wizard"""
        print("Running first-time setup...")

        hardware = self.profile_hardware()
        print(f"Detected hardware: {hardware}")

        models = await self.detect_ollama_models()
        print(f"Detected Ollama models: {models}")

        config = self.get_recommended_config(hardware, models)
        print(f"Recommended config: {json.dumps(config, indent=2)}")

        # Save config
        self.save_config(config)
        print(f"Configuration saved to {self.config_path}")

        return config

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
        return {}

    def save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)

    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []

        required_keys = ["ollama_host", "default_model", "max_memory_usage_gb"]
        for key in required_keys:
            if key not in config:
                issues.append(f"Missing required config key: {key}")

        if config.get("max_memory_usage_gb", 0) > 15.3:
            issues.append("Memory usage exceeds 15.3 GB limit")

        return issues

if __name__ == "__main__":
    import asyncio

    async def main():
        config_manager = AutoConfig()
        await config_manager.run_first_time_setup()

    asyncio.run(main())