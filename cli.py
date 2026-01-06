#!/usr/bin/env python3
"""
Basic CLI skeleton for Router Phase 1
"""

import argparse
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.config import AutoConfig
from backend.auth import auth_manager
import asyncio

def main():
    parser = argparse.ArgumentParser(description="Router Phase 1 CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Setup command
    subparsers.add_parser("setup", help="Run first-time setup")

    # Auth commands
    auth_parser = subparsers.add_parser("auth", help="Authentication commands")
    auth_subparsers = auth_parser.add_subparsers(dest="auth_command")

    login_parser = auth_subparsers.add_parser("login", help="Login to the system")
    login_parser.add_argument("username", help="Username")
    login_parser.add_argument("password", help="Password")

    # Placeholder for other commands
    subparsers.add_parser("chat", help="Chat interface (placeholder)")
    subparsers.add_parser("research", help="Research interface (placeholder)")
    subparsers.add_parser("rag", help="RAG management (placeholder)")

    args = parser.parse_args()

    if args.command == "setup":
        asyncio.run(run_setup())
    elif args.command == "auth":
        if args.auth_command == "login":
            login(args.username, args.password)
        else:
            auth_parser.print_help()
    else:
        parser.print_help()

async def run_setup():
    config_manager = AutoConfig()
    await config_manager.run_first_time_setup()

def login(username: str, password: str):
    user = auth_manager.authenticate_user(username, password)
    if user:
        token = auth_manager.create_access_token({"sub": user["username"], "user_id": user["id"]})
        print(f"Login successful for user: {username}")
        print(f"Access token: {token}")
        # In a real CLI, would save token to config
    else:
        print("Login failed: Invalid credentials")
        exit(1)

if __name__ == "__main__":
    main()