#!/usr/bin/env python
"""
Create timestamped backup of SQLite database.

Usage:
    python backend/scripts/backup_db.py [--backup-dir PATH]
"""

import argparse
import logging
import shutil
import sys
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("backup_db")


def backup_database(backup_dir: Path) -> Path:
    """
    Create timestamped backup of SQLite database.

    Args:
        backup_dir: Directory to store backup

    Returns:
        Path to backup file

    Raises:
        FileNotFoundError: If database file doesn't exist
    """
    # Parse database URL to get file path
    db_url = settings.DATABASE_URL
    if db_url.startswith("sqlite:///"):
        db_path = Path(db_url.replace("sqlite:///", ""))
        # Handle relative paths
        if not db_path.is_absolute():
            db_path = Path.cwd() / db_path
    else:
        raise ValueError(f"Unsupported database URL format: {db_url}")

    if not db_path.exists():
        raise FileNotFoundError(f"Database file not found: {db_path}")

    # Create backup directory if doesn't exist
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Generate timestamped backup filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_filename = f"backup_{timestamp}.db"
    backup_path = backup_dir / backup_filename

    # Copy database file
    logger.info(f"Creating backup: {db_path} → {backup_path}")
    shutil.copy2(db_path, backup_path)

    # Log backup info
    backup_size_mb = backup_path.stat().st_size / (1024 * 1024)
    logger.info(f"✓ Backup created: {backup_path}")
    logger.info(f"  Size: {backup_size_mb:.2f} MB")

    return backup_path


def main():
    """Main backup script entry point"""
    parser = argparse.ArgumentParser(description="Backup SQLite database")
    parser.add_argument(
        "--backup-dir",
        type=str,
        default="backups",
        help="Directory to store backups (default: backups)",
    )
    args = parser.parse_args()

    backup_dir = Path(args.backup_dir)

    try:
        backup_path = backup_database(backup_dir)
        logger.info(f"🎉 Backup complete: {backup_path}")

    except Exception as e:
        logger.error(f"❌ Backup failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
