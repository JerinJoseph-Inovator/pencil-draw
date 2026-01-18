"""
Configuration management using Pydantic settings.
Loads from environment variables with sensible defaults.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings with validation."""
    
    # API Settings
    app_name: str = "Pencil Draw API"
    version: str = "1.0.0"
    debug: bool = False
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000"]
    
    # File Upload Limits
    max_image_size_mb: int = 10
    max_resolution: int = 4096
    allowed_image_types: List[str] = ["image/jpeg", "image/png", "image/webp"]
    
    # Video Generation
    default_fps: int = 30
    min_duration: int = 1
    max_duration: int = 20
    video_quality_crf: int = 23  # Lower = better quality (18-28 range)
    
    # Temp File Management
    temp_dir: str = "temp"
    temp_file_retention_hours: int = 1
    
    # Processing
    edge_detection_threshold1: int = 50
    edge_detection_threshold2: int = 150
    gaussian_blur_kernel: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Singleton instance
settings = Settings()
