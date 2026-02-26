from __future__ import annotations

import os


def test_chatstore_new_chat_rag_enabled_by_default(tmp_path, monkeypatch) -> None:
    db = tmp_path / "chat.sqlite3"
    monkeypatch.setenv("CHAT_DB", str(db))

    # Import after env var so module-level CHAT_DB picks it up.
    from contextharbor.stores import chatstore

    chatstore.init_db()
    chat = chatstore.create_chat("t")
    prefs = chatstore.get_prefs(chat["id"])

    assert prefs["rag_enabled"] == 0
    assert prefs["doc_ids"] is None
