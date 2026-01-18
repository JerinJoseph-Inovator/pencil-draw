"""
Core sketch generation engine using OpenCV.
Converts images to edge maps with artistic styling.
"""
import cv2
import numpy as np
from PIL import Image
from typing import Tuple, List
from app.core.config import settings


class SketchEngine:
    """Handles image-to-sketch conversion."""
    
    def __init__(self):
        self.threshold1 = settings.edge_detection_threshold1
        self.threshold2 = settings.edge_detection_threshold2
        self.blur_kernel = (settings.gaussian_blur_kernel, settings.gaussian_blur_kernel)
    
    def generate_sketch(self, image: Image.Image) -> Tuple[np.ndarray, np.ndarray]:
        """
        Convert PIL image to sketch representation.
        
        Returns:
            Tuple of (edges array, original image as numpy array)
        """
        # Convert PIL to OpenCV format (RGB -> BGR)
        img_array = np.array(image)
        if len(img_array.shape) == 2:  # Grayscale
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
        elif img_array.shape[2] == 4:  # RGBA
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
        else:  # RGB
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Create sketch
        edges = self._edge_detection(img_bgr)
        
        return edges, img_bgr
    
    def _edge_detection(self, image: np.ndarray) -> np.ndarray:
        """
        Apply Canny edge detection with preprocessing.
        
        Returns:
            Binary edge map (white edges on black background)
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Reduce noise
        blurred = cv2.GaussianBlur(gray, self.blur_kernel, 0)
        
        # Detect edges
        edges = cv2.Canny(blurred, self.threshold1, self.threshold2)
        
        # Invert so edges are white on black
        edges = cv2.bitwise_not(edges)
        
        return edges
    
    def extract_stroke_paths(self, edges: np.ndarray) -> List[np.ndarray]:
        """
        Extract ordered stroke paths from edge map.
        Strokes are ordered for natural drawing flow (top-to-bottom, left-to-right).
        
        Returns:
            List of contours (stroke paths)
        """
        # Find contours
        contours, _ = cv2.findContours(
            cv2.bitwise_not(edges),  # Invert back for contour detection
            cv2.RETR_LIST,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Filter tiny noise contours
        min_area = 10
        filtered_contours = [c for c in contours if cv2.contourArea(c) > min_area]
        
        # Sort by Y position (top to bottom), then X (left to right)
        def contour_sort_key(contour):
            M = cv2.moments(contour)
            if M["m00"] == 0:
                return (0, 0)
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            return (cy, cx)
        
        sorted_contours = sorted(filtered_contours, key=contour_sort_key)
        
        return sorted_contours
    
    def get_drawing_points(self, contours: List[np.ndarray], max_points: int = 10000) -> np.ndarray:
        """
        Convert contours to ordered drawing points.
        
        Args:
            contours: List of contour arrays
            max_points: Maximum points to return (for performance)
        
        Returns:
            Array of (x, y) points in drawing order
        """
        all_points = []
        
        for contour in contours:
            # Reshape contour to 2D points
            points = contour.reshape(-1, 2)
            all_points.extend(points)
        
        # Limit total points if needed
        if len(all_points) > max_points:
            # Sample evenly
            step = len(all_points) // max_points
            all_points = all_points[::step]
        
        return np.array(all_points)


# Singleton instance
sketch_engine = SketchEngine()
