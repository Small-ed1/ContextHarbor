import sqlite3
import uuid
from typing import Any

from .database import Database
db = Database()


def list_chats(
    show_archived: bool = False, limit: int = 50, offset: int = 0
) -> list[dict[str, Any]]:
    """List all chats, optionally including archived ones."""
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        # For now, assume no archived, but can add later
        cursor.execute("""
            SELECT id, name, created_at, updated_at
            FROM chats
            ORDER BY updated_at DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))

        chats = []
        for row in cursor.fetchall():
            chat_id, name, created_at, updated_at = row
            chats.append({
                "id": chat_id,
                "title": name,
                "created_at": created_at,
                "summary": "",  # Can add summary field later
                "archived": False,
            })

        return chats


def create_chat() -> str:
    """Create a new chat and return its ID."""
    chat_id = str(uuid.uuid4())
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chats (id, name)
            VALUES (?, ?)
        """, (chat_id, "New Chat"))
        conn.commit()
    return chat_id


def get_chat(chat_id: str) -> dict[str, Any] | dict[str, str]:
    """Retrieve a chat by ID."""
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, created_at FROM chats WHERE id = ?", (chat_id,))
        row = cursor.fetchone()
        if row:
            chat_id, name, created_at = row
            # Get messages
            cursor.execute("""
                SELECT role, content, timestamp, token_count
                FROM messages
                WHERE chat_id = ?
                ORDER BY timestamp
            """, (chat_id,))
            messages = []
            for msg_row in cursor.fetchall():
                role, content, timestamp, token_count = msg_row
                messages.append({
                    "role": role,
                    "content": content,
                    "timestamp": timestamp,
                    "token_count": token_count or 0
                })
            return {
                "id": chat_id,
                "title": name,
                "created_at": created_at,
                "messages": messages,
            }
        return {"error": "Chat not found"}


def update_chat(chat_id: str, data: dict[str, Any]) -> dict[str, str]:
    """Update a chat with new data."""
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        # Update name if provided
        if "title" in data:
            cursor.execute("""
                UPDATE chats SET name = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (data["title"], chat_id))
            conn.commit()
            return {"status": "ok"}
        return {"error": "No valid update data provided"}


def delete_chat(chat_id: str) -> dict[str, str]:
    """Delete a chat by ID."""
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM chats WHERE id = ?", (chat_id,))
        if cursor.fetchone():
            cursor.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
            conn.commit()
            return {"status": "deleted"}
        return {"error": "Chat not found"}


def archive_chat(chat_id: str) -> dict[str, str]:
    """Archive a chat by ID."""
    # For now, just return status - can add archived field later
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM chats WHERE id = ?", (chat_id,))
        if cursor.fetchone():
            return {"status": "archived"}
        return {"error": "Chat not found"}


def add_message(chat_id: str, role: str, content: str, token_count: int = 0) -> bool:
    """Add a message to a chat."""
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO messages (chat_id, role, content, token_count)
            VALUES (?, ?, ?, ?)
        """, (chat_id, role, content, token_count))
        conn.commit()
        return cursor.rowcount > 0