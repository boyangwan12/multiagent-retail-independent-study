#!/usr/bin/env python
"""
Initialize database - create all tables.

Usage:
    python backend/scripts/init_db.py
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.db import Base, engine
# Import all models to ensure they're registered with Base
from app.database import models  # This imports all models from the models module

def init_database():
    """Create all database tables."""
    print("Creating database tables...")

    # Import all models to ensure they're registered with Base
    # This is important - SQLAlchemy needs to know about all models

    # Create all tables
    Base.metadata.create_all(bind=engine)

    print("✓ Database tables created successfully!")
    print(f"  Database: {engine.url}")
    print(f"  Tables: {', '.join(Base.metadata.tables.keys())}")

if __name__ == "__main__":
    init_database()
