"""
Session Manager
Handles file uploads and session-specific data storage for Streamlit UI
"""
import uuid
import shutil
from pathlib import Path
from typing import Optional, Tuple
from .data_loader import TrainingDataLoader


class SessionManager:
    """Manages user sessions and uploaded training data"""

    def __init__(self, base_dir: str = None):
        """
        Initialize session manager

        Args:
            base_dir: Base directory for storing session data.
                     Defaults to backend/tmp/sessions/
        """
        if base_dir is None:
            backend_dir = Path(__file__).parent.parent
            self.base_dir = backend_dir / "tmp" / "sessions"
        else:
            self.base_dir = Path(base_dir)

        # Create base directory if it doesn't exist
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def create_session(self) -> str:
        """
        Create a new session with unique ID

        Returns:
            session_id: Unique session identifier
        """
        session_id = str(uuid.uuid4())[:8]  # Use first 8 chars for readability
        session_dir = self.base_dir / f"session_{session_id}"
        session_dir.mkdir(parents=True, exist_ok=True)
        return session_id

    def get_session_dir(self, session_id: str) -> Path:
        """
        Get the directory path for a session

        Args:
            session_id: Session identifier

        Returns:
            Path to session directory
        """
        return self.base_dir / f"session_{session_id}"

    def save_uploaded_files(
        self,
        session_id: str,
        historical_sales_file,
        store_attributes_file
    ) -> Tuple[Path, Path]:
        """
        Save uploaded CSV files to session directory

        Args:
            session_id: Session identifier
            historical_sales_file: Uploaded historical sales CSV (UploadedFile object)
            store_attributes_file: Uploaded store attributes CSV (UploadedFile object)

        Returns:
            Tuple of (historical_path, store_attributes_path)
        """
        session_dir = self.get_session_dir(session_id)

        # Save historical sales
        historical_path = session_dir / "historical_sales_2022_2024.csv"
        with open(historical_path, 'wb') as f:
            f.write(historical_sales_file.getbuffer())

        # Save store attributes
        store_path = session_dir / "store_attributes.csv"
        with open(store_path, 'wb') as f:
            f.write(store_attributes_file.getbuffer())

        return historical_path, store_path

    def get_data_loader(self, session_id: str) -> TrainingDataLoader:
        """
        Get a data loader configured for this session's uploaded data

        Args:
            session_id: Session identifier

        Returns:
            TrainingDataLoader configured with session data
        """
        session_dir = self.get_session_dir(session_id)
        return TrainingDataLoader(data_dir=str(session_dir))

    def session_has_data(self, session_id: str) -> bool:
        """
        Check if a session has uploaded data files

        Args:
            session_id: Session identifier

        Returns:
            True if both required CSV files exist
        """
        session_dir = self.get_session_dir(session_id)
        historical_exists = (session_dir / "historical_sales_2022_2024.csv").exists()
        store_exists = (session_dir / "store_attributes.csv").exists()
        return historical_exists and store_exists

    def clear_session(self, session_id: str) -> None:
        """
        Delete all files for a session

        Args:
            session_id: Session identifier
        """
        session_dir = self.get_session_dir(session_id)
        if session_dir.exists():
            shutil.rmtree(session_dir)

    def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """
        Remove session directories older than max_age_hours

        Args:
            max_age_hours: Maximum age in hours before cleanup

        Returns:
            Number of sessions cleaned up
        """
        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        cleaned = 0

        for session_dir in self.base_dir.glob("session_*"):
            if session_dir.is_dir():
                dir_age = current_time - session_dir.stat().st_mtime
                if dir_age > max_age_seconds:
                    shutil.rmtree(session_dir)
                    cleaned += 1

        return cleaned
