import json
import os
import sqlite3
from pathlib import Path
from backend.database import Database
db = Database()
from backend.auth import AuthManager
auth_manager = AuthManager(db)

def migrate_chats():
    """Migrate existing chat JSON files to database"""
    chats_dir = Path("chats")
    if not chats_dir.exists():
        return

    for json_file in chats_dir.glob("*.json"):
        try:
            with open(json_file) as f:
                chat_data = json.load(f)

            # Create chat in database
            with sqlite3.connect(db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR IGNORE INTO chats (id, name, created_at)
                    VALUES (?, ?, ?)
                """, (
                    chat_data["id"],
                    chat_data.get("title", "Migrated Chat"),
                    chat_data.get("created_at")
                ))

                # Migrate messages
                for msg in chat_data.get("messages", []):
                    cursor.execute("""
                        INSERT INTO messages (chat_id, role, content, timestamp)
                        VALUES (?, ?, ?, ?)
                    """, (
                        chat_data["id"],
                        msg.get("role", "user"),
                        msg.get("content", ""),
                        msg.get("timestamp", chat_data.get("created_at"))
                    ))

                conn.commit()

            print(f"Migrated chat: {chat_data['id']}")

        except Exception as e:
            print(f"Failed to migrate {json_file}: {e}")

def migrate_config():
    """Migrate existing config files"""
    config_files = ["router.json", "server_config.json"]

    for config_file in config_files:
        if os.path.exists(config_file):
            try:
                with open(config_file) as f:
                    config_data = json.load(f)

                # Store in settings table for default user (id=1)
                with sqlite3.connect(db.db_path) as conn:
                    cursor = conn.cursor()
                    for key, value in config_data.items():
                        cursor.execute("""
                            INSERT OR REPLACE INTO settings (user_id, key, value)
                            VALUES (1, ?, ?)
                        """, (key, json.dumps(value)))
                    conn.commit()

                print(f"Migrated config: {config_file}")

            except Exception as e:
                print(f"Failed to migrate {config_file}: {e}")

if __name__ == "__main__":
    # Create a default admin user
    user_id = auth_manager.create_user("admin", "admin123")
    if user_id:
        print(f"Created default admin user with ID: {user_id}")

    migrate_chats()
    migrate_config()

    print("Migration completed")