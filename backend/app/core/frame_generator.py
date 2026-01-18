"""
Advanced Whiteboard Animation Frame Generator

DRAWING DIRECTIONS:
- left_to_right: Vertical lines sweeping from LEFT edge to RIGHT edge
- right_to_left: Vertical lines sweeping from RIGHT edge to LEFT edge  
- top_to_bottom: Horizontal lines sweeping from TOP edge to BOTTOM edge
- bottom_to_top: Horizontal lines sweeping from BOTTOM edge to TOP edge
- center_out: Spiral from center expanding outward
- element_by_element: Detect isolated objects, draw each one completely,
                      organized by row_wise (5 rows) or column_wise (5 columns)
"""
import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict
from app.core.config import settings
from app.core.element_by_element import element_drawer


class FrameGenerator:
    """Advanced whiteboard animation generator."""
    
    # Hand configurations: (filename, tip_x, tip_y, scale)
    HAND_CONFIGS: Dict[str, Tuple[str, int, int, float]] = {
        "hand_1": ("1.png", 66, 478, 0.3),
        "hand_2": ("2.png", 133, 720, 0.25),
        "hand_3": ("3.png", 80, 25, 0.3),
        "hand_4": ("4.png", 42, 235, 0.35),
    }
    
    def __init__(self):
        self.fps = settings.default_fps
        self.hands_dir = Path(__file__).parent.parent.parent / "assets" / "hands"
        self.hand_cache: Dict[str, Tuple[np.ndarray, int, int]] = {}
        self._preload_hands()
    
    def _preload_hands(self):
        """Load all hand images."""
        for style, (filename, tip_x, tip_y, scale) in self.HAND_CONFIGS.items():
            hand_path = self.hands_dir / filename
            if hand_path.exists():
                hand = cv2.imread(str(hand_path), cv2.IMREAD_UNCHANGED)
                if hand is not None:
                    if len(hand.shape) == 2:
                        hand = cv2.cvtColor(hand, cv2.COLOR_GRAY2BGRA)
                    elif hand.shape[2] == 3:
                        alpha = np.ones((hand.shape[0], hand.shape[1], 1), dtype=np.uint8) * 255
                        hand = np.concatenate([hand, alpha], axis=2)
                    
                    new_w = int(hand.shape[1] * scale)
                    new_h = int(hand.shape[0] * scale)
                    hand = cv2.resize(hand, (new_w, new_h), interpolation=cv2.INTER_AREA)
                    
                    self.hand_cache[style] = (hand, int(tip_x * scale), int(tip_y * scale))
        
        self.hand_cache["generated"] = self._create_generated_hand()
    
    def _create_generated_hand(self) -> Tuple[np.ndarray, int, int]:
        """Fallback programmatic hand."""
        size = 200
        tip_x, tip_y = 25, 175
        hand = np.zeros((size, size, 4), dtype=np.uint8)
        
        pencil_end = (size - 40, 30)
        cv2.line(hand, (tip_x, tip_y), pencil_end, (80, 210, 255, 255), 14)
        
        tip_pts = np.array([[tip_x - 6, tip_y - 20], [tip_x + 6, tip_y - 20], [tip_x, tip_y]], np.int32)
        cv2.fillPoly(hand, [tip_pts], (50, 50, 50, 255))
        
        ferrule = (int(tip_x + (pencil_end[0] - tip_x) * 0.8), int(tip_y + (pencil_end[1] - tip_y) * 0.8))
        cv2.ellipse(hand, ferrule, (9, 5), -55, 0, 360, (180, 180, 180, 255), -1)
        cv2.ellipse(hand, pencil_end, (10, 7), -55, 0, 360, (180, 160, 220, 255), -1)
        
        grip = (int(tip_x + (pencil_end[0] - tip_x) * 0.45), int(tip_y + (pencil_end[1] - tip_y) * 0.45))
        skin = (170, 190, 225, 245)
        cv2.ellipse(hand, grip, (48, 36), -55, 0, 360, skin, -1)
        
        return (hand, tip_x, tip_y)
    
    def _get_hand(self, style: str) -> Tuple[np.ndarray, int, int]:
        return self.hand_cache.get(style, self.hand_cache.get("generated", self._create_generated_hand()))
    
    def _get_hand_shake(self, frame_idx: int) -> Tuple[int, int]:
        """Subtle natural hand shake."""
        shake_x = int(2.5 * np.sin(frame_idx * 0.25) + 1.2 * np.sin(frame_idx * 0.6))
        shake_y = int(1.8 * np.sin(frame_idx * 0.35 + 0.5) + 1.0 * np.sin(frame_idx * 0.8))
        return shake_x, shake_y
    
    def generate_frames(
        self,
        original_image: np.ndarray,
        duration: int,
        hand_style: str = "hand_1",
        drawing_direction: str = "left_to_right",
        element_direction: str = "row_wise",
        drawing_mode: str = "normal"
    ) -> List[np.ndarray]:
        """Main entry point for frame generation."""
        total_frames = duration * self.fps
        hand_img, tip_x, tip_y = self._get_hand(hand_style)
        
        if drawing_mode == "outline_only":
            target = self._create_outline_image(original_image)
            return self._draw_with_direction(target, total_frames, drawing_direction, element_direction, hand_img, tip_x, tip_y)
        
        elif drawing_mode == "outline_then_fill":
            outline = self._create_outline_image(original_image)
            frames1 = self._draw_with_direction(outline, total_frames // 2, drawing_direction, element_direction, hand_img, tip_x, tip_y)
            frames2 = self._fill_color_over(outline, original_image, total_frames - total_frames // 2, drawing_direction, hand_img, tip_x, tip_y)
            return frames1 + frames2
        
        else:  # normal
            return self._draw_with_direction(original_image, total_frames, drawing_direction, element_direction, hand_img, tip_x, tip_y)
    
    def _create_outline_image(self, image: np.ndarray) -> np.ndarray:
        """Create sketch version."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 9, 75, 75)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 2)
        canny = cv2.bitwise_not(cv2.Canny(gray, 30, 100))
        combined = cv2.bitwise_and(edges, canny)
        return cv2.cvtColor(combined, cv2.COLOR_GRAY2BGR)
    
    def _draw_with_direction(
        self,
        target: np.ndarray,
        total_frames: int,
        direction: str,
        element_direction: str,
        hand_img: np.ndarray,
        tip_x: int,
        tip_y: int
    ) -> List[np.ndarray]:
        """Route to appropriate drawing method based on direction."""
        if direction == "element_by_element":
            # Use the new element_by_element module
            frames = element_drawer.draw_elements(
                target=target,
                total_frames=total_frames,
                element_direction=element_direction,
                hand_img=hand_img,
                tip_x=tip_x,
                tip_y=tip_y,
                composite_hand_func=self._composite_hand,
                get_hand_shake_func=self._get_hand_shake
            )
            if frames is None:
                # Fallback to left-to-right sweep if no elements detected
                return self._draw_sweep(target, total_frames, "left_to_right", hand_img, tip_x, tip_y)
            return frames
        else:
            return self._draw_sweep(target, total_frames, direction, hand_img, tip_x, tip_y)
    
    # ==================== SWEEP DIRECTIONS ====================
    
    def _draw_sweep(
        self,
        target: np.ndarray,
        total_frames: int,
        direction: str,
        hand_img: np.ndarray,
        tip_x: int,
        tip_y: int
    ) -> List[np.ndarray]:
        """
        Draw using sweep patterns.
        
        LEFT_TO_RIGHT: Pencil draws VERTICAL strokes, moving from left edge to right edge
        RIGHT_TO_LEFT: Pencil draws VERTICAL strokes, moving from right edge to left edge
        TOP_TO_BOTTOM: Pencil draws HORIZONTAL strokes, moving from top edge to bottom edge
        BOTTOM_TO_TOP: Pencil draws HORIZONTAL strokes, moving from bottom edge to top edge
        """
        h, w = target.shape[:2]
        white_bg = np.ones_like(target) * 255
        frames = []
        reveal_mask = np.zeros((h, w), dtype=np.uint8)
        
        path = self._create_sweep_path(w, h, total_frames, direction)
        brush_size = max(15, min(w, h) // 25)
        
        prev_x, prev_y = None, None
        
        for idx, (cx, cy) in enumerate(path):
            cx, cy = int(cx), int(cy)
            
            if prev_x is not None:
                cv2.line(reveal_mask, (prev_x, prev_y), (cx, cy), 255, brush_size * 2)
            cv2.circle(reveal_mask, (cx, cy), brush_size, 255, -1)
            
            prev_x, prev_y = cx, cy
            
            mask_3ch = cv2.GaussianBlur(reveal_mask, (5, 5), 0)[:, :, np.newaxis] / 255.0
            frame = (target * mask_3ch + white_bg * (1 - mask_3ch)).astype(np.uint8)
            
            shake_x, shake_y = self._get_hand_shake(idx)
            frame = self._composite_hand(frame, cx - tip_x + shake_x, cy - tip_y + shake_y, hand_img)
            frames.append(frame)
        
        # Final frames without hand
        for _ in range(int(self.fps * 0.3)):
            frames.append(target.copy())
        
        return frames
    
    def _create_sweep_path(self, w: int, h: int, total_frames: int, direction: str) -> List[Tuple[float, float]]:
        """
        Create path based on direction with CLEAR differences.
        """
        path = []
        margin = 5
        
        if direction == "left_to_right":
            # VERTICAL strokes moving LEFT to RIGHT
            # Pencil goes up-down in columns, columns progress left to right
            num_cols = max(8, w // 40)
            col_width = (w - 2 * margin) / num_cols
            frames_per_col = max(1, total_frames // num_cols)
            
            for col in range(num_cols):
                x = margin + col * col_width + col_width / 2
                go_down = (col % 2 == 0)
                
                for i in range(frames_per_col):
                    t = i / max(1, frames_per_col - 1)
                    if go_down:
                        y = margin + t * (h - 2 * margin)
                    else:
                        y = (h - margin) - t * (h - 2 * margin)
                    path.append((x, y))
        
        elif direction == "right_to_left":
            # VERTICAL strokes moving RIGHT to LEFT
            num_cols = max(8, w // 40)
            col_width = (w - 2 * margin) / num_cols
            frames_per_col = max(1, total_frames // num_cols)
            
            for col in range(num_cols - 1, -1, -1):  # Right to left
                x = margin + col * col_width + col_width / 2
                go_down = ((num_cols - 1 - col) % 2 == 0)
                
                for i in range(frames_per_col):
                    t = i / max(1, frames_per_col - 1)
                    if go_down:
                        y = margin + t * (h - 2 * margin)
                    else:
                        y = (h - margin) - t * (h - 2 * margin)
                    path.append((x, y))
        
        elif direction == "top_to_bottom":
            # HORIZONTAL strokes moving TOP to BOTTOM
            # Pencil goes left-right in rows, rows progress top to bottom
            num_rows = max(8, h // 40)
            row_height = (h - 2 * margin) / num_rows
            frames_per_row = max(1, total_frames // num_rows)
            
            for row in range(num_rows):
                y = margin + row * row_height + row_height / 2
                go_right = (row % 2 == 0)
                
                for i in range(frames_per_row):
                    t = i / max(1, frames_per_row - 1)
                    if go_right:
                        x = margin + t * (w - 2 * margin)
                    else:
                        x = (w - margin) - t * (w - 2 * margin)
                    path.append((x, y))
        
        elif direction == "bottom_to_top":
            # HORIZONTAL strokes moving BOTTOM to TOP
            num_rows = max(8, h // 40)
            row_height = (h - 2 * margin) / num_rows
            frames_per_row = max(1, total_frames // num_rows)
            
            for row in range(num_rows - 1, -1, -1):  # Bottom to top
                y = margin + row * row_height + row_height / 2
                go_right = ((num_rows - 1 - row) % 2 == 0)
                
                for i in range(frames_per_row):
                    t = i / max(1, frames_per_row - 1)
                    if go_right:
                        x = margin + t * (w - 2 * margin)
                    else:
                        x = (w - margin) - t * (w - 2 * margin)
                    path.append((x, y))
        
        elif direction == "center_out":
            # Spiral from center
            cx, cy = w // 2, h // 2
            max_radius = np.sqrt(cx**2 + cy**2)
            
            for i in range(total_frames):
                t = i / total_frames
                radius = t * max_radius
                angle = t * 14 * np.pi
                x = np.clip(cx + radius * np.cos(angle), margin, w - margin)
                y = np.clip(cy + radius * np.sin(angle), margin, h - margin)
                path.append((x, y))
        
        else:
            # Default to left_to_right
            return self._create_sweep_path(w, h, total_frames, "left_to_right")
        
        # Pad to total_frames
        while len(path) < total_frames:
            path.append(path[-1] if path else (w // 2, h // 2))
        
        return path[:total_frames]
    
    def _fill_color_over(
        self,
        outline: np.ndarray,
        color: np.ndarray,
        total_frames: int,
        direction: str,
        hand_img: np.ndarray,
        tip_x: int,
        tip_y: int
    ) -> List[np.ndarray]:
        """Fill color over outline."""
        h, w = outline.shape[:2]
        frames = []
        reveal_mask = np.zeros((h, w), dtype=np.uint8)
        
        path = self._create_sweep_path(w, h, total_frames, direction)
        brush_size = max(20, min(w, h) // 20)
        
        prev_x, prev_y = None, None
        
        for idx, (cx, cy) in enumerate(path):
            cx, cy = int(cx), int(cy)
            
            if prev_x is not None:
                cv2.line(reveal_mask, (prev_x, prev_y), (cx, cy), 255, brush_size * 2)
            cv2.circle(reveal_mask, (cx, cy), brush_size, 255, -1)
            prev_x, prev_y = cx, cy
            
            mask_3ch = cv2.GaussianBlur(reveal_mask, (7, 7), 0)[:, :, np.newaxis] / 255.0
            frame = (color * mask_3ch + outline * (1 - mask_3ch)).astype(np.uint8)
            
            shake_x, shake_y = self._get_hand_shake(idx)
            frame = self._composite_hand(frame, cx - tip_x + shake_x, cy - tip_y + shake_y, hand_img)
            frames.append(frame)
        
        for _ in range(int(self.fps * 0.3)):
            frames.append(color.copy())
        
        return frames
    
    def _composite_hand(
        self,
        frame: np.ndarray,
        hand_x: int,
        hand_y: int,
        hand_img: np.ndarray
    ) -> np.ndarray:
        """Overlay hand on frame."""
        hh, hw = hand_img.shape[:2]
        fh, fw = frame.shape[:2]
        
        src_x1, src_y1 = max(0, -hand_x), max(0, -hand_y)
        src_x2, src_y2 = min(hw, fw - hand_x), min(hh, fh - hand_y)
        dst_x1, dst_y1 = max(0, hand_x), max(0, hand_y)
        dst_x2, dst_y2 = dst_x1 + (src_x2 - src_x1), dst_y1 + (src_y2 - src_y1)
        
        if src_x2 <= src_x1 or src_y2 <= src_y1 or dst_x2 <= dst_x1 or dst_y2 <= dst_y1:
            return frame
        
        try:
            hand_region = hand_img[src_y1:src_y2, src_x1:src_x2]
            frame_region = frame[dst_y1:dst_y2, dst_x1:dst_x2]
            
            if hand_region.shape[:2] != frame_region.shape[:2]:
                return frame
            
            alpha = hand_region[:, :, 3:4] / 255.0
            blended = alpha * hand_region[:, :, :3] + (1 - alpha) * frame_region
            frame[dst_y1:dst_y2, dst_x1:dst_x2] = blended.astype(np.uint8)
        except:
            pass
        
        return frame


# Singleton
frame_generator = FrameGenerator()
