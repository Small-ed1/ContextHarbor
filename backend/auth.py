import json
import os
import secrets
import sqlite3
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import bcrypt
import jwt
from cryptography.fernet import Fernet

from backend.database import Database


class AuthManager:
    def __init__(self, db: Database):
        self.db = db
        secret_key = os.environ.get("JWT_SECRET")
        if not secret_key:
            raise ValueError("JWT_SECRET environment variable must be set for security")
        assert secret_key is not None  # For mypy
        self.secret_key = secret_key
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30

    def validate_password_strength(self, password: str) -> None:
        """Validate password meets minimum strength requirements."""
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in password):
            raise ValueError("Password must contain at least one digit")

    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.access_token_expire_minutes
            )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.PyJWTError:
            return None

    def validate_password(self, password: str) -> None:
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        # Add more validation as needed

    def create_user(
        self, username: str, password: str, profile: Optional[Dict[str, Any]] = None
    ) -> Optional[int]:
        self.validate_password(password)
        hashed_password = self.hash_password(password)
        profile_json = json.dumps(profile) if profile else None

        with sqlite3.connect(self.db.db_path) as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO users (username, password_hash, profile)
                    VALUES (?, ?, ?)
                """,
                    (username, hashed_password, profile_json),
                )
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                return None  # Username already exists

    def authenticate_user(
        self, username: str, password: str
    ) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, password_hash, profile FROM users WHERE username = ?",
                (username,),
            )
            row = cursor.fetchone()

            if row and self.verify_password(password, row[1]):
                user_id, _, profile_json = row
                profile = json.loads(profile_json) if profile_json else {}
                return {"id": user_id, "username": username, "profile": profile}
        return None

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, profile FROM users WHERE id = ?", (user_id,)
            )
            row = cursor.fetchone()

            if row:
                user_id, username, profile_json = row
                profile = json.loads(profile_json) if profile_json else {}
                return {"id": user_id, "username": username, "profile": profile}
        return None

    def update_user_profile(self, user_id: int, profile: Dict[str, Any]) -> bool:
        profile_json = json.dumps(profile)
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE users SET profile = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """,
                (profile_json, user_id),
            )
            conn.commit()
            return cursor.rowcount > 0


# Encrypted bypass tokens for CLI access
import secrets

from cryptography.fernet import Fernet


class TokenManager:
    def __init__(self):
        key = os.environ.get("TOKEN_ENCRYPTION_KEY")
        if not key:
            raise ValueError("TOKEN_ENCRYPTION_KEY environment variable must be set for token persistence")
        assert key is not None  # For mypy
        self.key = key.encode() if isinstance(key, str) else key
        self.cipher = Fernet(self.key)

    def generate_bypass_token(self, user_id: int) -> str:
        token_data = f"{user_id}:{secrets.token_urlsafe(32)}"
        return self.cipher.encrypt(token_data.encode()).decode()

    def verify_bypass_token(self, token: str) -> Optional[int]:
        try:
            decrypted = self.cipher.decrypt(token.encode()).decode()
            user_id, _ = decrypted.split(":", 1)
            return int(user_id)
        except Exception:
            return None


# Global instances
db = Database()
auth_manager = AuthManager(db)
token_manager = TokenManager()


