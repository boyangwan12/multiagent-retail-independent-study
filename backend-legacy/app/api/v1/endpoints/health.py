from fastapi import APIRouter, status
from datetime import datetime
from sqlalchemy import text
from contextlib import contextmanager

router = APIRouter()

@contextmanager
def get_db_session():
    """Context manager for database sessions"""
    from app.database.db import SessionLocal
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint - returns API status and connectivity"""

    # Check database connectivity
    db_status = "ok"
    try:
        with get_db_session() as session:
            session.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "version": "0.1.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "services": {
            "database": db_status,
            "api": "ok",
        },
    }
