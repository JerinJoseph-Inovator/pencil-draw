"""
Input validation utilities.
"""
import base64
import io
from PIL import Image
from typing import Tuple
from app.core.config import settings


class ValidationError(Exception):
    """Custom validation error with error code."""
    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code
        super().__init__(self.message)


def validate_image(image_base64: str) -> Tuple[Image.Image, str]:
    """
    Validate and decode base64 image.
    
    Returns:
        Tuple of (PIL Image object, image format)
    
    Raises:
        ValidationError: If validation fails
    """
    try:
        # Decode base64
        image_data = base64.b64decode(image_base64)
        
        # Check size
        size_mb = len(image_data) / (1024 * 1024)
        if size_mb > settings.max_image_size_mb:
            raise ValidationError(
                f"Image too large. Max {settings.max_image_size_mb}MB allowed.",
                "IMAGE_SIZE_EXCEEDED"
            )
        
        # Open with PIL
        image = Image.open(io.BytesIO(image_data))
        
        # Validate format
        if image.format.lower() not in ['jpeg', 'jpg', 'png', 'webp']:
            raise ValidationError(
                f"Unsupported format: {image.format}. Use JPEG, PNG, or WebP.",
                "UNSUPPORTED_FORMAT"
            )
        
        # Check resolution
        width, height = image.size
        if width > settings.max_resolution or height > settings.max_resolution:
            raise ValidationError(
                f"Image resolution too high. Max {settings.max_resolution}px per dimension.",
                "RESOLUTION_EXCEEDED"
            )
        
        # Validate it's not corrupted
        image.verify()
        
        # Reopen after verify (verify() closes the file)
        image = Image.open(io.BytesIO(image_data))
        
        return image, image.format.lower()
    
    except base64.binascii.Error:
        raise ValidationError("Invalid base64 encoding.", "INVALID_BASE64")
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"Image validation failed: {str(e)}", "VALIDATION_ERROR")


def validate_duration(duration: int) -> int:
    """Validate video duration."""
    if not settings.min_duration <= duration <= settings.max_duration:
        raise ValidationError(
            f"Duration must be between {settings.min_duration}-{settings.max_duration} seconds.",
            "INVALID_DURATION"
        )
    return duration
