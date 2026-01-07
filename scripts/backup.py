#!/usr/bin/env python3
"""
Backup script for Router Phase 1 vector indices and documents.
Creates timestamped backups of vector store data and uploaded documents.
"""

import os
import shutil
import datetime
from pathlib import Path
import logging
import argparse
import subprocess
import tempfile

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BackupManager:
    """Manages backup operations for vector store and documents."""

    def __init__(self, base_dir: str = "data", backup_dir: str = "backups"):
        self.base_dir = Path(base_dir)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, name: str = None, encrypt_password: str = None) -> str:
        """Create a backup with optional custom name.

        Args:
            name: Optional custom name for the backup

        Returns:
            Path to the created backup directory
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        if name:
            backup_name = f"{name}_{timestamp}"
        else:
            backup_name = f"backup_{timestamp}"

        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Creating backup: {backup_path}")

        # Backup vector store
        vector_store_dir = self.base_dir / "vector_store"
        if vector_store_dir.exists():
            backup_vector_dir = backup_path / "vector_store"
            shutil.copytree(vector_store_dir, backup_vector_dir)
            logger.info(f"Backed up vector store to {backup_vector_dir}")
        else:
            logger.warning("Vector store directory not found, skipping")

        # Backup documents
        documents_dir = self.base_dir / "documents"
        if documents_dir.exists():
            backup_docs_dir = backup_path / "documents"
            shutil.copytree(documents_dir, backup_docs_dir)
            logger.info(f"Backed up documents to {backup_docs_dir}")
        else:
            logger.warning("Documents directory not found, skipping")

        # Create backup metadata
        metadata = {
            "timestamp": timestamp,
            "backup_name": backup_name,
            "vector_store_backed_up": vector_store_dir.exists(),
            "documents_backed_up": documents_dir.exists(),
            "created_at": datetime.datetime.now().isoformat(),
        }

        metadata_file = backup_path / "backup_info.json"
        import json
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        # Encrypt backup if password provided
        if encrypt_password:
            encrypted_path = self._encrypt_backup(backup_path, encrypt_password)
            # Remove plain backup
            shutil.rmtree(backup_path)
            backup_path = encrypted_path
            logger.info(f"Backup encrypted: {backup_path}")

        logger.info(f"Backup completed: {backup_path}")
        return str(backup_path)

    def list_backups(self) -> list:
        """List all available backups."""
        backups = []
        if self.backup_dir.exists():
            for item in self.backup_dir.iterdir():
                if item.is_dir() and item.name.startswith(('backup_',)):
                    metadata_file = item / "backup_info.json"
                    if metadata_file.exists():
                        try:
                            import json
                            with open(metadata_file, 'r') as f:
                                metadata = json.load(f)
                            backups.append(metadata)
                        except Exception as e:
                            logger.warning(f"Failed to read metadata for {item}: {e}")
                            backups.append({
                                "backup_name": item.name,
                                "path": str(item),
                                "error": "Invalid metadata"
                            })
                    else:
                        backups.append({
                            "backup_name": item.name,
                            "path": str(item),
                            "note": "No metadata file"
                        })

        return sorted(backups, key=lambda x: x.get('created_at', ''), reverse=True)

    def _encrypt_backup(self, backup_path: Path, password: str) -> Path:
        """Encrypt the backup directory using tar and gpg."""
        tar_path = backup_path.with_suffix('.tar.gz')
        encrypted_path = tar_path.with_suffix('.gpg')

        # Create tar.gz
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_tar = Path(temp_dir) / tar_path.name
            try:
                # Create tar.gz
                subprocess.run([
                    'tar', 'czf', str(temp_tar), '-C', str(backup_path.parent), backup_path.name
                ], check=True)

                # Encrypt with gpg
                with open(temp_tar, 'rb') as infile, open(encrypted_path, 'wb') as outfile:
                    subprocess.run([
                        'gpg', '--symmetric', '--batch', '--yes', '--passphrase', password, '--output', '-'
                    ], stdin=infile, stdout=outfile, check=True)

                logger.info(f"Backup encrypted to {encrypted_path}")
                return encrypted_path

            except subprocess.CalledProcessError as e:
                logger.error(f"Encryption failed: {e}")
                raise

    def cleanup_old_backups(self, keep_count: int = 10):
        """Clean up old backups, keeping the most recent ones.

        Args:
            keep_count: Number of most recent backups to keep
        """
        backups = self.list_backups()
        if len(backups) <= keep_count:
            return

        to_remove = backups[keep_count:]
        for backup in to_remove:
            backup_path = Path(backup['path'])
            try:
                shutil.rmtree(backup_path)
                logger.info(f"Removed old backup: {backup_path}")
            except Exception as e:
                logger.error(f"Failed to remove {backup_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Backup vector store and documents")
    parser.add_argument("--name", help="Custom name for the backup")
    parser.add_argument("--encrypt-password", help="Encrypt backup with symmetric password")
    parser.add_argument("--list", action="store_true", help="List available backups")
    parser.add_argument("--cleanup", type=int, metavar="COUNT", help="Clean up old backups, keeping COUNT most recent")

    args = parser.parse_args()

    backup_manager = BackupManager()

    if args.list:
        backups = backup_manager.list_backups()
        if not backups:
            print("No backups found.")
        else:
            print("Available backups:")
            for backup in backups:
                print(f"  {backup['backup_name']} - {backup.get('created_at', 'Unknown time')}")
                if 'error' in backup:
                    print(f"    Error: {backup['error']}")
    elif args.cleanup:
        backup_manager.cleanup_old_backups(args.cleanup)
        print(f"Cleaned up old backups, keeping {args.cleanup} most recent.")
    else:
        backup_path = backup_manager.create_backup(args.name, args.encrypt_password)
        print(f"Backup created: {backup_path}")

if __name__ == "__main__":
    main()