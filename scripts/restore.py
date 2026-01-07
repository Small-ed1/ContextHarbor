#!/usr/bin/env python3
"""
Restore script for Router Phase 1 backups.
Restores vector store and documents from a backup.
"""

import os
import shutil
import json
from pathlib import Path
import logging
import argparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RestoreManager:
    """Manages restore operations."""

    def __init__(self, base_dir: str = "data", backup_dir: str = "backups"):
        self.base_dir = Path(base_dir)
        self.backup_dir = Path(backup_dir)

    def list_backups(self) -> list:
        """List all available backups."""
        backups = []
        if self.backup_dir.exists():
            for item in self.backup_dir.iterdir():
                if item.is_dir() and (item.name.startswith('backup_') or '_' in item.name):
                    metadata_file = item / "backup_info.json"
                    if metadata_file.exists():
                        try:
                            with open(metadata_file, 'r') as f:
                                metadata = json.load(f)
                            backups.append(metadata)
                        except Exception as e:
                            logger.warning(f"Failed to read metadata for {item}: {e}")
                    else:
                        # Create basic metadata for backups without info file
                        backups.append({
                            "backup_name": item.name,
                            "path": str(item),
                            "created_at": item.stat().st_mtime,
                            "note": "Legacy backup"
                        })

        return sorted(backups, key=lambda x: x.get('created_at', 0), reverse=True)

    def restore_backup(self, backup_name: str, dry_run: bool = False) -> bool:
        """Restore from a specific backup.

        Args:
            backup_name: Name of the backup to restore
            dry_run: If True, only show what would be done

        Returns:
            True if restore successful
        """
        backup_path = self.backup_dir / backup_name
        if not backup_path.exists():
            logger.error(f"Backup not found: {backup_path}")
            return False

        logger.info(f"Restoring from backup: {backup_name}")
        if dry_run:
            logger.info("DRY RUN - No changes will be made")

        success = True

        # Restore vector store
        backup_vector_dir = backup_path / "vector_store"
        target_vector_dir = self.base_dir / "vector_store"
        if backup_vector_dir.exists():
            if dry_run:
                logger.info(f"Would restore vector store from {backup_vector_dir} to {target_vector_dir}")
            else:
                # Backup current if exists
                if target_vector_dir.exists():
                    backup_current = target_vector_dir.with_suffix('.backup')
                    if backup_current.exists():
                        shutil.rmtree(backup_current)
                    shutil.move(str(target_vector_dir), str(backup_current))
                    logger.info(f"Backed up current vector store to {backup_current}")

                shutil.copytree(backup_vector_dir, target_vector_dir)
                logger.info(f"Restored vector store to {target_vector_dir}")
        else:
            logger.warning("No vector store in backup")

        # Restore documents
        backup_docs_dir = backup_path / "documents"
        target_docs_dir = self.base_dir / "documents"
        if backup_docs_dir.exists():
            if dry_run:
                logger.info(f"Would restore documents from {backup_docs_dir} to {target_docs_dir}")
            else:
                # Create target dir if needed
                target_docs_dir.mkdir(parents=True, exist_ok=True)
                # Copy files, but don't overwrite existing unless different
                for item in backup_docs_dir.rglob('*'):
                    if item.is_file():
                        relative_path = item.relative_to(backup_docs_dir)
                        target_file = target_docs_dir / relative_path
                        target_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, target_file)
                        logger.debug(f"Restored document: {relative_path}")
                logger.info(f"Restored documents to {target_docs_dir}")
        else:
            logger.warning("No documents in backup")

        if not dry_run:
            # Verify restore
            success = self.verify_restore(backup_name)
            if success:
                logger.info("Restore completed successfully")
            else:
                logger.error("Restore verification failed")

        return success

    def verify_restore(self, backup_name: str) -> bool:
        """Verify that the restore was successful.

        Args:
            backup_name: Name of the backup that was restored

        Returns:
            True if verification passes
        """
        backup_path = self.backup_dir / backup_name
        issues = []

        # Check vector store
        target_vector_dir = self.base_dir / "vector_store"
        backup_vector_dir = backup_path / "vector_store"
        if backup_vector_dir.exists():
            if not target_vector_dir.exists():
                issues.append("Vector store directory not restored")
            else:
                # Check key files
                index_file = target_vector_dir / "vector_index.faiss"
                metadata_file = target_vector_dir / "metadata.json"
                if not index_file.exists():
                    issues.append("Vector index file missing")
                if not metadata_file.exists():
                    issues.append("Metadata file missing")

                # Try to load metadata
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r') as f:
                            json.load(f)
                    except Exception as e:
                        issues.append(f"Invalid metadata file: {e}")

        # Check documents
        target_docs_dir = self.base_dir / "documents"
        backup_docs_dir = backup_path / "documents"
        if backup_docs_dir.exists():
            if not target_docs_dir.exists():
                issues.append("Documents directory not restored")
            else:
                # Count files
                backup_files = list(backup_docs_dir.rglob('*'))
                backup_files = [f for f in backup_files if f.is_file()]
                restored_files = list(target_docs_dir.rglob('*'))
                restored_files = [f for f in restored_files if f.is_file()]

                if len(backup_files) != len(restored_files):
                    issues.append(f"File count mismatch: {len(restored_files)} restored vs {len(backup_files)} in backup")

        if issues:
            logger.error("Restore verification failed:")
            for issue in issues:
                logger.error(f"  - {issue}")
            return False

        logger.info("Restore verification passed")
        return True

def main():
    parser = argparse.ArgumentParser(description="Restore from backup")
    parser.add_argument("backup_name", nargs='?', help="Name of the backup to restore")
    parser.add_argument("--list", action="store_true", help="List available backups")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be restored without making changes")
    parser.add_argument("--verify", metavar="BACKUP_NAME", help="Verify a specific backup")

    args = parser.parse_args()

    restore_manager = RestoreManager()

    if args.list:
        backups = restore_manager.list_backups()
        if not backups:
            print("No backups found.")
        else:
            print("Available backups:")
            for backup in backups:
                print(f"  {backup['backup_name']} - {backup.get('created_at', 'Unknown time')}")
    elif args.verify:
        success = restore_manager.verify_restore(args.verify)
        print(f"Verification {'passed' if success else 'failed'}")
    elif args.backup_name:
        success = restore_manager.restore_backup(args.backup_name, dry_run=args.dry_run)
        if args.dry_run:
            print("Dry run completed.")
        else:
            print(f"Restore {'successful' if success else 'failed'}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()