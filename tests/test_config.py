import pytest
import tempfile
import os
import json
from backend.config import AutoConfig

def test_config_loading():
    """Test config loading and saving"""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = os.path.join(temp_dir, "config.json")

        # Create config manager
        from pathlib import Path
        config_manager = AutoConfig()
        config_manager.config_path = Path(config_path)

        # Save config
        test_config = {"theme": "dark", "model": "llama3.2:latest"}
        config_manager.save_config(test_config)

        # Load config
        loaded_config = config_manager.load_config()
        assert loaded_config == test_config

        print("Config loading test passed")

def test_hardware_profiling():
    """Test hardware profiling"""
    config_manager = AutoConfig()
    hardware = config_manager.profile_hardware()

    # Check required keys
    required_keys = ["cpu_count", "memory_total_gb", "disk_total_gb"]
    for key in required_keys:
        assert key in hardware
        assert hardware[key] > 0

    # Memory should be reasonable (not zero or negative)
    assert 1 <= hardware["memory_total_gb"] <= 1000  # Reasonable range

    print("Hardware profiling test passed")

def test_config_validation():
    """Test config validation"""
    config_manager = AutoConfig()

    # Valid config
    valid_config = {
        "ollama_host": "http://localhost:11434",
        "default_model": "llama3.2:latest",
        "max_memory_usage_gb": 12.0
    }
    issues = config_manager.validate_config(valid_config)
    assert len(issues) == 0

    # Invalid config - missing required
    invalid_config = {"theme": "dark"}
    issues = config_manager.validate_config(invalid_config)
    assert len(issues) > 0

    # Invalid config - memory too high
    high_memory_config = valid_config.copy()
    high_memory_config["max_memory_usage_gb"] = 20.0
    issues = config_manager.validate_config(high_memory_config)
    assert len(issues) > 0

    print("Config validation test passed")

if __name__ == "__main__":
    test_config_loading()
    test_hardware_profiling()
    test_config_validation()
    print("All config tests passed")