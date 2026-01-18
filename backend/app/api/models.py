"""
Pydantic models for request/response validation.
"""
from pydantic import BaseModel, Field, validator
from typing import Literal, Optional


class GenerateRequest(BaseModel):
    """Request model for video generation."""
    
    image: str = Field(..., description="Base64 encoded image data")
    duration: int = Field(..., ge=1, le=20, description="Video duration in seconds")
    hand_style: str = Field(default="hand_1", description="Hand overlay style identifier")
    
    # Section 4: Drawing Direction (for sweep modes)
    drawing_direction: Literal[
        "left_to_right",
        "right_to_left",
        "top_to_bottom",
        "bottom_to_top",
        "center_out",
        "element_by_element"
    ] = Field(default="left_to_right", description="Direction of drawing animation")
    
    # Section 5: Element Direction (only used when drawing_direction is element_by_element)
    element_direction: Literal[
        "default",
        "row_wise",
        "column_wise"
    ] = Field(default="default", description="Element organization: default (top-half then bottom-half), row_wise (5 rows) or column_wise (5 columns)")
    
    # Section 6: Drawing Mode
    drawing_mode: Literal[
        "normal",
        "outline_only",
        "outline_then_fill"
    ] = Field(default="normal", description="Drawing style mode")
    
    # Section 7: Output Format
    output_format: Literal["mp4", "gif"] = Field(default="mp4", description="Output video format")
    
    @validator('image')
    def validate_image_format(cls, v):
        """Ensure image is valid base64."""
        if not v or len(v) < 100:
            raise ValueError("Invalid image data")
        # Remove data URL prefix if present
        if v.startswith('data:image'):
            v = v.split(',', 1)[1] if ',' in v else v
        return v
    
    @validator('hand_style')
    def validate_hand_style(cls, v):
        """Validate hand style exists."""
        allowed_styles = [
            "hand_1",
            "hand_2",
            "hand_3",
            "hand_4",
            "generated"
        ]
        if v not in allowed_styles:
            raise ValueError(f"Hand style must be one of: {', '.join(allowed_styles)}")
        return v


class GenerateResponse(BaseModel):
    """Response model for successful generation."""
    
    status: Literal["success"] = "success"
    video_url: str = Field(..., description="URL to download generated video")
    file_id: str = Field(..., description="Unique file identifier")
    duration_actual: float = Field(..., description="Actual video duration in seconds")
    frames_generated: int = Field(..., description="Total frames created")
    file_size_mb: Optional[float] = Field(None, description="Output file size in MB")


class ErrorResponse(BaseModel):
    """Response model for errors."""
    
    status: Literal["error"] = "error"
    message: str = Field(..., description="Human-readable error message")
    code: str = Field(..., description="Machine-readable error code")


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str = "healthy"
    version: str
    temp_files_count: int = 0
