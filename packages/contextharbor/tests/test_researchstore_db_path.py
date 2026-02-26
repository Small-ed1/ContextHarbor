from __future__ import annotations

import importlib


def test_researchstore_expands_tilde_env_db_path(tmp_path, monkeypatch) -> None:
    # Use a tilde path to mirror common shell configs.
    # Point HOME to tmp so ~ expands there.
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("RESEARCH_DB", "~/.contextharbor_test/research.sqlite3")

    from contextharbor.stores import researchstore as _researchstore

    researchstore = importlib.reload(_researchstore)
    researchstore.init_db()

    p = researchstore._db_path()
    assert p.endswith("/research.sqlite3")
