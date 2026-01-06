import pytest
import tempfile
import os
from backend.database import Database
from backend.auth import AuthManager

def test_auth_user_creation():
    """Test user creation and authentication"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        db = Database(db_path)
        auth = AuthManager(db)

        # Create user
        user_id = auth.create_user("testuser", "password123")
        assert user_id is not None

        # Authenticate user
        user = auth.authenticate_user("testuser", "password123")
        assert user is not None
        assert user["username"] == "testuser"
        assert user["id"] == user_id

        # Wrong password
        user_wrong = auth.authenticate_user("testuser", "wrongpass")
        assert user_wrong is None

        # Non-existent user
        user_none = auth.authenticate_user("nonexistent", "password123")
        assert user_none is None

        print("User creation and authentication test passed")
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)

def test_password_hashing():
    """Test password hashing and verification"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        db = Database(db_path)
        auth = AuthManager(db)

        password = "mysecretpassword"

        # Hash password
        hashed = auth.hash_password(password)
        assert hashed != password

        # Verify correct password
        assert auth.verify_password(password, hashed)

        # Verify wrong password
        assert not auth.verify_password("wrongpassword", hashed)

        print("Password hashing test passed")
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)

def test_jwt_tokens():
    """Test JWT token creation and verification"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        db = Database(db_path)
        auth = AuthManager(db)

        # Create token
        data = {"user_id": 123, "username": "testuser"}
        token = auth.create_access_token(data)
        assert token is not None

        # Verify token
        decoded = auth.verify_token(token)
        assert decoded is not None
        assert decoded["user_id"] == 123
        assert decoded["username"] == "testuser"

        # Invalid token
        invalid_decoded = auth.verify_token("invalid.token.here")
        assert invalid_decoded is None

        print("JWT token test passed")
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)

if __name__ == "__main__":
    test_auth_user_creation()
    test_password_hashing()
    test_jwt_tokens()
    print("All auth tests passed")