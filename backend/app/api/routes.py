"""
API route handlers.
"""
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse
import uuid
import asyncio
import traceback
import cv2
import numpy as np
from pathlib import Path
from app.api.models import (
    GenerateRequest,
    GenerateResponse,
    ErrorResponse,
    HealthResponse
)
from app.utils.validators import validate_image, validate_duration, ValidationError
from app.utils.file_manager import file_manager
from app.core.frame_generator import frame_generator
from app.core.video_exporter import video_exporter
from app.core.config import settings


router = APIRouter()


@router.post(
    "/generate",
    response_model=GenerateResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def generate_video(request: GenerateRequest):
    """
    Generate whiteboard-style hand-drawn animation from image.
    
    Supports multiple drawing directions and modes:
    - Directions: left-to-right, right-to-left, top-to-bottom, bottom-to-top, center-out, element-by-element
    - Modes: normal (full color), outline only (sketch), outline then fill
    """
    try:
        # Validate inputs
        pil_image, img_format = validate_image(request.image)
        validate_duration(request.duration)
        
        # Create unique file ID
        file_id = uuid.uuid4().hex[:12]
        
        # Convert PIL image to BGR (OpenCV format)
        img_array = np.array(pil_image)
        if len(img_array.shape) == 2:  # Grayscale
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
        elif img_array.shape[2] == 4:  # RGBA
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
        else:  # RGB
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Generate animation frames with advanced options
        frames = frame_generator.generate_frames(
            original_image=img_bgr,
            duration=request.duration,
            hand_style=request.hand_style,
            drawing_direction=request.drawing_direction,
            element_direction=request.element_direction,
            drawing_mode=request.drawing_mode
        )
        
        # Export video
        output_path = file_manager.get_file_path(file_id, request.output_format)
        
        if request.output_format == "mp4":
            result = video_exporter.export_mp4(frames, output_path)
        else:  # gif
            result = video_exporter.export_gif(frames, output_path)
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail={"status": "error", "message": result["error"], "code": "EXPORT_FAILED"}
            )
        
        # Cleanup old files asynchronously
        asyncio.create_task(asyncio.to_thread(file_manager.cleanup_old_files))
        
        return GenerateResponse(
            video_url=f"/api/download/{file_id}.{request.output_format}",
            file_id=file_id,
            duration_actual=result["duration"],
            frames_generated=result["frames_count"],
            file_size_mb=result["file_size_mb"]
        )
    
    except ValidationError as e:
        raise HTTPException(
            status_code=400,
            detail={"status": "error", "message": e.message, "code": e.code}
        )
    except Exception as e:
        # Print detailed traceback for debugging
        print("=" * 80)
        print("ERROR in /api/generate:")
        print(traceback.format_exc())
        print("=" * 80)
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "message": str(e), "code": "INTERNAL_ERROR"}
        )


@router.get("/download/{file_name}")
async def download_video(file_name: str):
    """
    Download generated video file.
    
    Args:
        file_name: Filename with extension (e.g., abc123.mp4)
    """
    file_path = file_manager.temp_dir / file_name
    
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail={"status": "error", "message": "File not found", "code": "FILE_NOT_FOUND"}
        )
    
    # Determine media type
    media_type = "video/mp4" if file_name.endswith(".mp4") else "image/gif"
    
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=f"pencil_draw_{file_name}",
        headers={
            "Cache-Control": "no-cache",
            "Content-Disposition": f"attachment; filename=pencil_draw_{file_name}"
        }
    )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring."""
    temp_count = file_manager.count_temp_files()
    
    return HealthResponse(
        status="healthy",
        version=settings.version,
        temp_files_count=temp_count
    )
