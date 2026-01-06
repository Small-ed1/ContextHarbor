import pytest
from memory_manager import load_memories, save_memories


def test_load_memories_empty():
    memories = load_memories()
    assert isinstance(memories, list)


def test_save_and_load_memories(tmp_path, monkeypatch):
    from pathlib import Path

    test_file = tmp_path / "test_memories.json"
    monkeypatch.setattr("memory_manager.MEMORIES_PATH", test_file)

    test_memories = [{"key": "test", "value": "data"}]
    save_memories(test_memories)

    loaded = load_memories()
    assert loaded == test_memories


def test_save_memories_overwrite(tmp_path, monkeypatch):
    from pathlib import Path

    test_file = tmp_path / "test_memories.json"
    monkeypatch.setattr("memory_manager.MEMORIES_PATH", test_file)

    save_memories([{"key": "old", "value": "old"}])
    save_memories([{"key": "new", "value": "new"}])

    loaded = load_memories()
    assert loaded == [{"key": "new", "value": "new"}]
