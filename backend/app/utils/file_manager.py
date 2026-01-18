"""
Temporary file management with automatic cleanup.
"""
import os
import time
import uuid
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from app.core.config import settings


class FileManager:
    """Manages temporary files with auto-cleanup."""
    
    def __init__(self):
        self.temp_dir = Path(settings.temp_dir)
        self.temp_dir.mkdir(exist_ok=True)
    
    def create_temp_dir(self) -> Path:
        """Create a unique temporary directory for a job."""
        job_id = uuid.uuid4().hex
        job_dir = self.temp_dir / job_id
        job_dir.mkdir(exist_ok=True)
        return job_dir
    
    def cleanup_old_files(self) -> int:
        """
        Remove files older than retention period.
        Returns count of deleted files.
        """
        if not self.temp_dir.exists():
            return 0
        
        cutoff_time = time.time() - (settings.temp_file_retention_hours * 3600)
        deleted_count = 0
        
        for item in self.temp_dir.iterdir():
            try:
                # Check modification time
                if item.stat().st_mtime < cutoff_time:
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
                    deleted_count += 1
            except Exception as e:
                print(f"Error cleaning up {item}: {e}")
                continue
        
        return deleted_count
    
    def get_file_path(self, file_id: str, extension: str = "mp4") -> Path:
        """Get path for output file."""
        return self.temp_dir / f"{file_id}.{extension}"
    
    def count_temp_files(self) -> int:
        """Count current temp files/directories."""
        if not self.temp_dir.exists():
            return 0
        return len(list(self.temp_dir.iterdir()))


# Singleton instance
file_manager = FileManager()
