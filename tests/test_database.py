import pytest
import sqlite3
import os
import tempfile
from backend.database import Database

def test_database_creation():
    """Test database initialization"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        db = Database(db_path)

        # Check tables exist
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            expected_tables = [
                'users', 'chats', 'messages', 'knowledge', 'embeddings',
                'research_sessions', 'settings', 'migrations',
                'knowledge_fts', 'messages_fts'
            ]

            for table in expected_tables:
                assert table in tables, f"Table {table} not found"

        print("Database creation test passed")
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)

def test_user_crud():
    """Test basic user CRUD operations"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        db = Database(db_path)

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Create user
            cursor.execute("""
                INSERT INTO users (username, password_hash, profile)
                VALUES (?, ?, ?)
            """, ("testuser", "hash123", '{"role": "admin"}'))
            user_id = cursor.lastrowid

            # Read user
            cursor.execute("SELECT username, profile FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            assert row[0] == "testuser"
            assert row[1] == '{"role": "admin"}'

            # Update user
            cursor.execute("""
                UPDATE users SET profile = ? WHERE id = ?
            """, ('{"role": "user"}', user_id))
            conn.commit()

            # Verify update
            cursor.execute("SELECT profile FROM users WHERE id = ?", (user_id,))
            assert cursor.fetchone()[0] == '{"role": "user"}'

            # Delete user
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()

            # Verify deletion
            cursor.execute("SELECT COUNT(*) FROM users WHERE id = ?", (user_id,))
            assert cursor.fetchone()[0] == 0

        print("User CRUD test passed")
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)

if __name__ == "__main__":
    test_database_creation()
    test_user_crud()
    print("All database tests passed")