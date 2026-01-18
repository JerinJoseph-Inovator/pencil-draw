"""
Video export using FFmpeg.
Handles MP4 and GIF generation with proper codec settings.
"""
import subprocess
import cv2
import os
import shutil
from pathlib import Path
from typing import List, Optional
import numpy as np
from app.core.config import settings


class VideoExporter:
    """Exports frames to video files using FFmpeg."""
    
    def __init__(self):
        self.fps = settings.default_fps
        self.crf = settings.video_quality_crf
        self.ffmpeg_cmd = self._find_ffmpeg()
    
    def _find_ffmpeg(self) -> str:
        """Find FFmpeg executable in system PATH or common locations."""
        # First try system PATH
        ffmpeg_path = shutil.which('ffmpeg')
        if ffmpeg_path:
            return ffmpeg_path
        
        # Common Windows installation paths
        common_paths = [
            r"C:\Users\jerin\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe",
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        # Default to 'ffmpeg' and let it fail with clear error
        return 'ffmpeg'
    
    def export_mp4(
        self,
        frames: List[np.ndarray],
        output_path: Path,
        fps: Optional[int] = None
    ) -> dict:
        """
        Export frames to MP4 using FFmpeg.
        
        Args:
            frames: List of BGR numpy arrays
            output_path: Path to save MP4 file
            fps: Frames per second (optional, uses default if None)
        
        Returns:
            dict with video metadata
        """
        if fps is None:
            fps = self.fps
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create temporary frame directory
        temp_frames_dir = output_path.parent / f"{output_path.stem}_frames"
        temp_frames_dir.mkdir(exist_ok=True)
        
        try:
            # Save frames as images
            for idx, frame in enumerate(frames):
                frame_path = temp_frames_dir / f"frame_{idx:05d}.png"
                cv2.imwrite(str(frame_path), frame)
            
            # FFmpeg command with scale filter to ensure even dimensions
            # libx264 requires width and height to be divisible by 2
            ffmpeg_command = [
                self.ffmpeg_cmd,
                '-y',  # Overwrite output
                '-framerate', str(fps),
                '-i', str(temp_frames_dir / 'frame_%05d.png'),
                '-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2',  # Pad to even dimensions
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', str(self.crf),
                '-pix_fmt', 'yuv420p',  # Compatibility with most players
                '-movflags', '+faststart',  # Enable web streaming
                str(output_path)
            ]
            
            # Run FFmpeg
            result = subprocess.run(
                ffmpeg_command,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Get file size
            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            
            return {
                "success": True,
                "output_path": str(output_path),
                "frames_count": len(frames),
                "duration": len(frames) / fps,
                "file_size_mb": round(file_size_mb, 2),
                "fps": fps
            }
        
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"FFmpeg error: {e.stderr}"
            }
        
        finally:
            # Cleanup temp frames
            self._cleanup_dir(temp_frames_dir)
    
    def export_gif(
        self,
        frames: List[np.ndarray],
        output_path: Path,
        fps: Optional[int] = None
    ) -> dict:
        """
        Export frames to GIF using FFmpeg with optimization.
        
        Args:
            frames: List of BGR numpy arrays
            output_path: Path to save GIF file
            fps: Frames per second (optional, uses default if None)
        
        Returns:
            dict with video metadata
        """
        if fps is None:
            fps = min(self.fps, 15)  # Limit GIF to 15fps for size
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create temporary frame directory
        temp_frames_dir = output_path.parent / f"{output_path.stem}_frames"
        temp_frames_dir.mkdir(exist_ok=True)
        
        try:
            # Save frames
            for idx, frame in enumerate(frames):
                frame_path = temp_frames_dir / f"frame_{idx:05d}.png"
                cv2.imwrite(str(frame_path), frame)
            
            # FFmpeg command with palette generation for better quality
            palette_path = temp_frames_dir / "palette.png"
            
            # Generate palette
            palette_cmd = [
                self.ffmpeg_cmd,
                '-y',
                '-framerate', str(fps),
                '-i', str(temp_frames_dir / 'frame_%05d.png'),
                '-vf', 'palettegen=stats_mode=diff',
                str(palette_path)
            ]
            subprocess.run(palette_cmd, capture_output=True, check=True)
            
            # Create GIF using palette
            gif_cmd = [
                self.ffmpeg_cmd,
                '-y',
                '-framerate', str(fps),
                '-i', str(temp_frames_dir / 'frame_%05d.png'),
                '-i', str(palette_path),
                '-lavfi', 'paletteuse=dither=bayer:bayer_scale=5',
                str(output_path)
            ]
            subprocess.run(gif_cmd, capture_output=True, check=True)
            
            # Get file size
            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            
            return {
                "success": True,
                "output_path": str(output_path),
                "frames_count": len(frames),
                "duration": len(frames) / fps,
                "file_size_mb": round(file_size_mb, 2),
                "fps": fps
            }
        
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"FFmpeg error: {e.stderr}"
            }
        
        finally:
            # Cleanup temp frames
            self._cleanup_dir(temp_frames_dir)
    
    def _cleanup_dir(self, directory: Path):
        """Remove directory and all contents."""
        if directory.exists():
            import shutil
            shutil.rmtree(directory)


# Singleton instance
video_exporter = VideoExporter()
