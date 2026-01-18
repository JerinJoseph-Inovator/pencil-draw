"""
Element-by-Element Drawing Logic

This module handles intelligent detection and drawing of isolated elements/objects
in an image. Elements are organized into rows or columns based on their START position.

ELEMENT DIRECTION OPTIONS:
- default: Divide screen into 2 halves (top and bottom). 
           Draw order: Top-half elements (left-to-right), then Bottom-half elements (left-to-right)

- row_wise: Divide screen into 5 rows. Elements assigned to rows by their TOP edge.
            Draw order: Row 1 (left-to-right), Row 2 (left-to-right), ... Row 5 (left-to-right)
            
- column_wise: Divide screen into 5 columns. Elements assigned to columns by their LEFT edge.
               Draw order: Col 1 (top-to-bottom), Col 2 (top-to-bottom), ... Col 5 (top-to-bottom)

If an element spans multiple rows/columns (e.g., covers rows 2,3,4), it is assigned
to the row/column where it STARTS (top edge for rows, left edge for columns).
The entire element is drawn completely before moving to the next element.
"""
import cv2
import numpy as np
from typing import List, Tuple, Dict
from dataclasses import dataclass


@dataclass
class DetectedElement:
    """Represents a detected element/object in the image."""
    mask: np.ndarray
    bbox: Tuple[int, int, int, int]  # (x, y, width, height)
    area: int
    centroid: Tuple[float, float]
    
    @property
    def x(self) -> int:
        return self.bbox[0]
    
    @property
    def y(self) -> int:
        return self.bbox[1]
    
    @property
    def width(self) -> int:
        return self.bbox[2]
    
    @property
    def height(self) -> int:
        return self.bbox[3]
    
    @property
    def top(self) -> int:
        """Top edge Y coordinate (for row assignment)."""
        return self.bbox[1]
    
    @property
    def left(self) -> int:
        """Left edge X coordinate (for column assignment)."""
        return self.bbox[0]
    
    @property
    def center_x(self) -> float:
        return self.bbox[0] + self.bbox[2] / 2
    
    @property
    def center_y(self) -> float:
        return self.bbox[1] + self.bbox[3] / 2


class ElementByElementDrawer:
    """
    Handles element-by-element drawing with row-wise or column-wise organization.
    """
    
    NUM_DIVISIONS = 5  # Number of rows or columns
    
    def __init__(self, fps: int = 30):
        self.fps = fps
    
    def detect_elements(self, image: np.ndarray) -> List[DetectedElement]:
        """
        Detect all closed/isolated objects in the image.
        Uses multiple detection methods for robust element finding.
        """
        h, w = image.shape[:2]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Method 1: Simple thresholding (for high contrast images)
        _, thresh1 = cv2.threshold(gray, 245, 255, cv2.THRESH_BINARY_INV)
        _, thresh2 = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY_INV)
        
        # Method 2: Adaptive thresholding (for varying illumination)
        adaptive = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 25, 8
        )
        
        # Method 3: Edge detection (for outline-based images)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        edges_dilated = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=2)
        
        # Method 4: Color-based segmentation
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        _, saturation_mask = cv2.threshold(hsv[:, :, 1], 30, 255, cv2.THRESH_BINARY)
        
        # Combine all detection methods
        combined = cv2.bitwise_or(thresh1, thresh2)
        combined = cv2.bitwise_or(combined, adaptive)
        combined = cv2.bitwise_or(combined, edges_dilated)
        combined = cv2.bitwise_or(combined, saturation_mask)
        
        # Morphological cleanup
        kernel = np.ones((3, 3), np.uint8)
        combined = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel, iterations=4)
        combined = cv2.morphologyEx(combined, cv2.MORPH_OPEN, kernel, iterations=2)
        
        # Fill holes in detected regions
        contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        filled = np.zeros_like(combined)
        cv2.drawContours(filled, contours, -1, 255, -1)
        
        # Find connected components
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            filled, connectivity=8
        )
        
        # Filter by size
        min_area = (h * w) // 500   # Min 0.2% of image
        max_area = int((h * w) * 0.8)  # Max 80% of image
        
        elements = []
        
        for label_id in range(1, num_labels):  # Skip background (0)
            area = stats[label_id, cv2.CC_STAT_AREA]
            
            if min_area < area < max_area:
                x = stats[label_id, cv2.CC_STAT_LEFT]
                y = stats[label_id, cv2.CC_STAT_TOP]
                bw = stats[label_id, cv2.CC_STAT_WIDTH]
                bh = stats[label_id, cv2.CC_STAT_HEIGHT]
                
                # Create element mask
                mask = np.zeros((h, w), dtype=np.uint8)
                mask[labels == label_id] = 255
                
                # Dilate mask slightly for smoother edges
                mask = cv2.dilate(mask, kernel, iterations=3)
                
                elements.append(DetectedElement(
                    mask=mask,
                    bbox=(x, y, bw, bh),
                    area=area,
                    centroid=(centroids[label_id][0], centroids[label_id][1])
                ))
        
        return elements
    
    def organize_by_rows(
        self, 
        elements: List[DetectedElement], 
        image_height: int
    ) -> List[List[DetectedElement]]:
        """
        Organize elements into 5 rows based on their TOP edge (start position).
        
        An element that spans rows 2,3,4 is assigned to row 2 (where it starts).
        Within each row, elements are sorted left-to-right by X position.
        """
        row_height = image_height / self.NUM_DIVISIONS
        rows: List[List[DetectedElement]] = [[] for _ in range(self.NUM_DIVISIONS)]
        
        for elem in elements:
            # Assign to row based on TOP edge
            row_idx = min(int(elem.top / row_height), self.NUM_DIVISIONS - 1)
            rows[row_idx].append(elem)
        
        # Sort each row by left edge (X position) - left to right
        for row in rows:
            row.sort(key=lambda e: e.left)
        
        return rows
    
    def organize_by_columns(
        self, 
        elements: List[DetectedElement], 
        image_width: int
    ) -> List[List[DetectedElement]]:
        """
        Organize elements into 5 columns based on their LEFT edge (start position).
        
        An element that spans columns 2,3,4 is assigned to column 2 (where it starts).
        Within each column, elements are sorted top-to-bottom by Y position.
        """
        col_width = image_width / self.NUM_DIVISIONS
        columns: List[List[DetectedElement]] = [[] for _ in range(self.NUM_DIVISIONS)]
        
        for elem in elements:
            # Assign to column based on LEFT edge
            col_idx = min(int(elem.left / col_width), self.NUM_DIVISIONS - 1)
            columns[col_idx].append(elem)
        
        # Sort each column by top edge (Y position) - top to bottom
        for col in columns:
            col.sort(key=lambda e: e.top)
        
        return columns
    
    def organize_by_halves(
        self,
        elements: List[DetectedElement],
        image_height: int
    ) -> List[List[DetectedElement]]:
        """
        Organize elements into 2 halves (top and bottom) based on their TOP edge.
        
        This is the DEFAULT mode - simple top-half then bottom-half organization.
        Within each half, elements are sorted left-to-right by X position.
        """
        center_y = image_height / 2
        halves: List[List[DetectedElement]] = [[], []]  # [top_half, bottom_half]
        
        for elem in elements:
            # Assign to half based on TOP edge (where element starts)
            if elem.top < center_y:
                halves[0].append(elem)  # Top half
            else:
                halves[1].append(elem)  # Bottom half
        
        # Sort each half by left edge (X position) - left to right
        for half in halves:
            half.sort(key=lambda e: e.left)
        
        return halves
    
    def get_ordered_elements(
        self, 
        elements: List[DetectedElement], 
        image_width: int,
        image_height: int,
        direction: str = "default"
    ) -> List[DetectedElement]:
        """
        Get elements in drawing order based on direction.
        
        Args:
            elements: List of detected elements
            image_width: Width of the image
            image_height: Height of the image
            direction: "default", "row_wise" or "column_wise"
            
        Returns:
            Flattened list of elements in drawing order
        """
        if direction == "column_wise":
            organized = self.organize_by_columns(elements, image_width)
        elif direction == "row_wise":
            organized = self.organize_by_rows(elements, image_height)
        else:  # default - top/bottom halves
            organized = self.organize_by_halves(elements, image_height)
        
        # Flatten the organized structure
        ordered = []
        for group in organized:
            ordered.extend(group)
        
        return ordered
    
    def create_element_fill_path(
        self, 
        element: DetectedElement, 
        num_frames: int
    ) -> List[Tuple[float, float]]:
        """
        Create drawing path to fill an element's bounding box.
        Uses horizontal zigzag pattern within the element area.
        """
        x, y, w, h = element.bbox
        path = []
        
        num_rows = max(4, h // 12)
        row_height = h / num_rows
        frames_per_row = max(1, num_frames // num_rows)
        
        for row in range(num_rows):
            row_y = y + row * row_height + row_height / 2
            go_right = (row % 2 == 0)
            
            for i in range(frames_per_row):
                t = i / max(1, frames_per_row - 1)
                if go_right:
                    row_x = x + t * w
                else:
                    row_x = x + w - t * w
                path.append((row_x, row_y))
        
        # Ensure we have enough frames
        while len(path) < num_frames:
            path.append(path[-1] if path else (x + w / 2, y + h / 2))
        
        return path[:num_frames]
    
    def create_travel_path(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        num_frames: int
    ) -> List[Tuple[float, float]]:
        """
        Create smooth path for pencil traveling between elements.
        Uses ease-in-out interpolation for natural motion.
        """
        path = []
        sx, sy = start
        ex, ey = end
        
        for i in range(num_frames):
            t = i / max(1, num_frames - 1)
            # Smooth ease-in-out
            t = t * t * (3 - 2 * t)
            x = sx + (ex - sx) * t
            y = sy + (ey - sy) * t
            path.append((x, y))
        
        return path
    
    def draw_elements(
        self,
        target: np.ndarray,
        total_frames: int,
        element_direction: str,
        hand_img: np.ndarray,
        tip_x: int,
        tip_y: int,
        composite_hand_func,
        get_hand_shake_func
    ) -> List[np.ndarray]:
        """
        Main drawing method for element-by-element mode.
        
        Args:
            target: Target image to reveal
            total_frames: Total number of frames for animation
            element_direction: "row_wise" or "column_wise"
            hand_img: Hand overlay image
            tip_x, tip_y: Pencil tip coordinates in hand image
            composite_hand_func: Function to composite hand onto frame
            get_hand_shake_func: Function to get hand shake offset
            
        Returns:
            List of animation frames
        """
        h, w = target.shape[:2]
        white_bg = np.ones_like(target) * 255
        
        # Detect elements
        elements = self.detect_elements(target)
        
        if not elements:
            # No elements found - return None to signal fallback needed
            return None
        
        # Get ordered elements based on direction
        ordered_elements = self.get_ordered_elements(
            elements, w, h, element_direction
        )
        
        if not ordered_elements:
            return None
        
        # Calculate frame allocation
        num_elements = len(ordered_elements)
        travel_frames_per = max(5, total_frames // (num_elements * 10))
        draw_frames_per = max(10, (total_frames - travel_frames_per * num_elements) // num_elements)
        
        frames = []
        cumulative_mask = np.zeros((h, w), dtype=np.uint8)
        last_pos = None
        
        for elem_idx, element in enumerate(ordered_elements):
            # Calculate start position for this element
            start_x = element.x + element.width // 2
            start_y = element.y
            
            # Travel animation from last position to this element
            if last_pos is not None:
                travel_path = self.create_travel_path(
                    last_pos, (start_x, start_y), travel_frames_per
                )
                for tx, ty in travel_path:
                    # Keep current reveal state during travel
                    mask_3ch = cv2.GaussianBlur(cumulative_mask, (5, 5), 0)
                    mask_3ch = mask_3ch[:, :, np.newaxis] / 255.0
                    frame = (target * mask_3ch + white_bg * (1 - mask_3ch)).astype(np.uint8)
                    
                    shake_x, shake_y = get_hand_shake_func(len(frames))
                    frame = composite_hand_func(
                        frame, int(tx) - tip_x + shake_x, 
                        int(ty) - tip_y + shake_y, hand_img
                    )
                    frames.append(frame)
            
            # Calculate frames for this element
            remaining = total_frames - len(frames)
            remaining_elements = num_elements - elem_idx
            remaining_travels = remaining_elements - 1
            elem_frames = min(
                draw_frames_per,
                max(10, (remaining - travel_frames_per * remaining_travels) // remaining_elements)
            )
            
            # Draw this element
            elem_path = self.create_element_fill_path(element, elem_frames)
            current_reveal = np.zeros((h, w), dtype=np.uint8)
            
            brush_size = max(8, min(element.width, element.height) // 8)
            prev_x, prev_y = None, None
            
            for px, py in elem_path:
                px_int, py_int = int(px), int(py)
                
                # Draw stroke
                if prev_x is not None:
                    cv2.line(current_reveal, (prev_x, prev_y), (px_int, py_int), 255, brush_size * 2)
                cv2.circle(current_reveal, (px_int, py_int), brush_size, 255, -1)
                prev_x, prev_y = px_int, py_int
                
                # Combine masks - only reveal within element area
                elem_reveal = cv2.bitwise_and(current_reveal, element.mask)
                combined = cv2.bitwise_or(cumulative_mask, elem_reveal)
                
                mask_3ch = cv2.GaussianBlur(combined, (5, 5), 0)
                mask_3ch = mask_3ch[:, :, np.newaxis] / 255.0
                frame = (target * mask_3ch + white_bg * (1 - mask_3ch)).astype(np.uint8)
                
                shake_x, shake_y = get_hand_shake_func(len(frames))
                frame = composite_hand_func(
                    frame, px_int - tip_x + shake_x, 
                    py_int - tip_y + shake_y, hand_img
                )
                frames.append(frame)
            
            # Add this element to cumulative mask
            cumulative_mask = cv2.bitwise_or(cumulative_mask, element.mask)
            last_pos = (prev_x, prev_y)
        
        # Final frames without hand
        final_hold = int(self.fps * 0.3)
        for _ in range(final_hold):
            frames.append(target.copy())
        
        return frames
    
    def get_debug_visualization(
        self, 
        image: np.ndarray, 
        element_direction: str = "row_wise"
    ) -> np.ndarray:
        """
        Create debug visualization showing detected elements and their organization.
        Useful for testing and debugging element detection.
        """
        h, w = image.shape[:2]
        debug_img = image.copy()
        
        elements = self.detect_elements(image)
        ordered = self.get_ordered_elements(elements, w, h, element_direction)
        
        # Draw division lines
        if element_direction == "row_wise":
            row_height = h / self.NUM_DIVISIONS
            for i in range(1, self.NUM_DIVISIONS):
                y = int(i * row_height)
                cv2.line(debug_img, (0, y), (w, y), (0, 255, 255), 2)
        else:
            col_width = w / self.NUM_DIVISIONS
            for i in range(1, self.NUM_DIVISIONS):
                x = int(i * col_width)
                cv2.line(debug_img, (x, 0), (x, h), (0, 255, 255), 2)
        
        # Draw elements with numbers
        colors = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255), 
            (255, 255, 0), (255, 0, 255), (0, 255, 255)
        ]
        
        for idx, elem in enumerate(ordered):
            color = colors[idx % len(colors)]
            x, y, bw, bh = elem.bbox
            
            # Draw bounding box
            cv2.rectangle(debug_img, (x, y), (x + bw, y + bh), color, 2)
            
            # Draw order number
            cv2.putText(
                debug_img, str(idx + 1), 
                (x + 5, y + 25), cv2.FONT_HERSHEY_SIMPLEX, 
                0.8, color, 2
            )
        
        return debug_img


# Module-level instance
element_drawer = ElementByElementDrawer()
