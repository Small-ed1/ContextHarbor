import pytest
from config_manager import get_default_config, load_config, save_config


def test_get_default_config():
    config = get_default_config()
    assert isinstance(config, dict)
    assert "theme" in config
    assert config["theme"] == "dark"


def test_load_config():
    config = load_config()
    assert isinstance(config, dict)


def test_save_config(tmp_path, monkeypatch):
    # Use tmp_path for testing
    from pathlib import Path

    test_file = tmp_path / "test_router.json"
    monkeypatch.setattr(
        "config_manager.Path", lambda x: test_file if x == "router.json" else Path(x)
    )

    test_config = {"theme": "light"}
    save_config(test_config)

    loaded = load_config()
    assert loaded["theme"] == "light"


def test_config_update():
    # Test partial update
    original = load_config()
    save_config({"theme": "dark"})
    updated = load_config()
    assert updated["theme"] == "dark"
    # Other defaults should remain
    assert "temperature" in updated


def test_invalid_config_file(tmp_path, monkeypatch):
    from pathlib import Path

    test_file = tmp_path / "test_router.json"
    # Write invalid JSON
    test_file.write_text("{invalid json")
    monkeypatch.setattr(
        "config_manager.Path", lambda x: test_file if x == "router.json" else Path(x)
    )

    config = load_config()
    # Should fall back to defaults
    assert isinstance(config, dict)
    assert "theme" in config
