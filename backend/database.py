import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional


class Database:
    def __init__(self, db_path: str = "router.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("PRAGMA cache_size=-64000;")  # 64MB cache
            conn.execute("PRAGMA temp_store=MEMORY;")
            conn.execute("PRAGMA mmap_size=268435456;")  # 256MB mmap

            # Create tables
            self._create_tables(conn)
            self._create_indexes(conn)
            self._create_fts_tables(conn)
            self._create_migrations_table(conn)

    def _create_tables(self, conn):
        # Users table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                profile TEXT,  -- JSON string
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Chats table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chats (
                id TEXT PRIMARY KEY,
                user_id INTEGER,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """
        )

        # Messages table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                role TEXT NOT NULL,  -- 'user', 'assistant', 'system'
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                token_count INTEGER DEFAULT 0,
                metadata TEXT,  -- JSON string
                FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE
            )
        """
        )

        # Knowledge base table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                source TEXT,
                chunk_id TEXT,
                metadata TEXT,  -- JSON string
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Embeddings table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                knowledge_id INTEGER NOT NULL,
                embedding BLOB NOT NULL,
                model TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (knowledge_id) REFERENCES knowledge(id) ON DELETE CASCADE
            )
        """
        )

        # Research sessions table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS research_sessions (
                id TEXT PRIMARY KEY,
                user_id INTEGER,
                query TEXT NOT NULL,
                status TEXT DEFAULT 'pending',  -- 'pending', 'running', 'completed', 'failed'
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                results TEXT,  -- JSON string
                config TEXT,  -- JSON string
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """
        )

        # Settings table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                key TEXT NOT NULL,
                value TEXT,
                UNIQUE(user_id, key),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """
        )

    def _create_indexes(self, conn):
        # Indexes for performance
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages(chat_id)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_knowledge_source ON knowledge(source)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_embeddings_knowledge_id ON embeddings(knowledge_id)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_research_sessions_user_id ON research_sessions(user_id)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_research_sessions_status ON research_sessions(status)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_settings_user_id ON settings(user_id)"
        )

    def _create_fts_tables(self, conn):
        # FTS5 virtual table for knowledge search
        conn.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts USING fts5(
                content, source, metadata,
                content=knowledge,
                content_rowid=id
            )
        """
        )

        # FTS5 virtual table for messages search
        conn.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
                content,
                content=messages,
                content_rowid=id
            )
        """
        )

        # Triggers to keep FTS tables in sync
        conn.execute(
            """
            CREATE TRIGGER IF NOT EXISTS knowledge_fts_insert AFTER INSERT ON knowledge
            BEGIN
                INSERT INTO knowledge_fts(rowid, content, source, metadata)
                VALUES (new.id, new.content, new.source, new.metadata);
            END
        """
        )

        conn.execute(
            """
            CREATE TRIGGER IF NOT EXISTS knowledge_fts_delete AFTER DELETE ON knowledge
            BEGIN
                DELETE FROM knowledge_fts WHERE rowid = old.id;
            END
        """
        )

        conn.execute(
            """
            CREATE TRIGGER IF NOT EXISTS knowledge_fts_update AFTER UPDATE ON knowledge
            BEGIN
                UPDATE knowledge_fts SET
                    content = new.content,
                    source = new.source,
                    metadata = new.metadata
                WHERE rowid = new.id;
            END
        """
        )

        conn.execute(
            """
            CREATE TRIGGER IF NOT EXISTS messages_fts_insert AFTER INSERT ON messages
            BEGIN
                INSERT INTO messages_fts(rowid, content)
                VALUES (new.id, new.content);
            END
        """
        )

        conn.execute(
            """
            CREATE TRIGGER IF NOT EXISTS messages_fts_delete AFTER DELETE ON messages
            BEGIN
                DELETE FROM messages_fts WHERE rowid = old.id;
            END
        """
        )

        conn.execute(
            """
            CREATE TRIGGER IF NOT EXISTS messages_fts_update AFTER UPDATE ON messages
            BEGIN
                UPDATE messages_fts SET content = new.content WHERE rowid = new.id;
            END
        """
        )

    def _create_migrations_table(self, conn):
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )


# Migration system placeholder
class MigrationManager:
    def __init__(self, db: Database):
        self.db = db

    def apply_migration(self, name: str, sql: str):
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM migrations WHERE name = ?", (name,))
            if cursor.fetchone():
                return  # Already applied

            conn.executescript(sql)
            conn.execute("INSERT INTO migrations (name) VALUES (?)", (name,))
            conn.commit()


# Initialize database
db = Database()

# Example migration
mm = MigrationManager(db)
# Add migrations as needed

if __name__ == "__main__":
    print(f"Database initialized at {db.db_path}")
