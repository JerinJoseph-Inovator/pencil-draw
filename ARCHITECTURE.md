# System Architecture Document

## Core Algorithm Explained

### Overview
The sketch animation generation follows a pipeline approach with 5 distinct stages:

```
Input Image → Edge Detection → Stroke Ordering → Frame Generation → Video Export
```

---

## Stage 1: Edge Detection (sketch_engine.py)

### Canny Edge Detection Algorithm

**Purpose:** Convert photographic image into line-art sketch

**Process:**
1. **Grayscale Conversion**
   - Reduces 3-channel RGB to single-channel intensity
   - Simplifies gradient calculations
   - Formula: `Gray = 0.299*R + 0.587*G + 0.114*B`

2. **Gaussian Blur (5×5 kernel)**
   - Reduces noise that creates false edges
   - Applies weighted average of neighboring pixels
   - Kernel size is tunable (default: 5×5)

3. **Gradient Calculation**
   - Uses Sobel operators to find intensity gradients
   - Horizontal gradient: `Gx = dI/dx`
   - Vertical gradient: `Gy = dI/dy`
   - Magnitude: `G = √(Gx² + Gy²)`
   - Direction: `θ = arctan(Gy/Gx)`

4. **Non-Maximum Suppression**
   - Thins edges to single-pixel width
   - Only keeps local maxima in gradient direction
   - Prevents thick, blurry edges

5. **Double Threshold**
   - High threshold (150): Strong edges
   - Low threshold (50): Weak edges
   - Weak edges kept only if connected to strong edges

**Output:** Binary edge map (white lines on black background)

**Tunability:**
```python
threshold1 = 50   # Lower = more detail, more noise
threshold2 = 150  # Higher = cleaner, fewer edges
```

---

## Stage 2: Stroke Path Extraction (sketch_engine.py)

### Contour Detection & Ordering

**Purpose:** Convert edge map into drawable stroke paths with natural drawing order

**Process:**

1. **Contour Detection**
   ```python
   contours = cv2.findContours(
       edges,
       cv2.RETR_LIST,      # All contours at same hierarchy
       cv2.CHAIN_APPROX_SIMPLE  # Compress horizontal/vertical segments
   )
   ```
   - Finds connected edge components
   - Each contour = continuous stroke path

2. **Noise Filtering**
   - Remove contours with area < 10 pixels
   - Eliminates speckles from noise

3. **Natural Drawing Order**
   ```python
   def contour_sort_key(contour):
       M = cv2.moments(contour)
       cx = M["m10"] / M["m00"]  # Centroid X
       cy = M["m01"] / M["m00"]  # Centroid Y
       return (cy, cx)  # Sort by Y (top→bottom), then X (left→right)
   ```
   - Simulates human drawing: top to bottom, left to right
   - Uses contour centroids for positioning

4. **Point Extraction**
   - Flatten contours into ordered (x, y) points
   - Optional: Downsample to max 10,000 points for performance
   - Even sampling maintains visual quality

**Output:** Ordered array of drawable points

---

## Stage 3: Frame Generation (frame_generator.py)

### Progressive Reveal Animation

**Purpose:** Create illusion of real-time drawing

**Process:**

1. **Frame Calculation**
   ```python
   total_frames = duration * fps  # e.g., 10s * 30fps = 300 frames
   points_per_frame = total_points / total_frames
   ```

2. **Per-Frame Rendering**
   ```python
   for frame_idx in range(total_frames):
       visible_points = all_points[:frame_idx * points_per_frame]
       
       # Draw accumulated strokes
       for (x, y) in visible_points:
           canvas[y, x] = BLACK  # Draw single pixel
       
       # Add hand overlay (with lag)
       hand_pos = visible_points[-20]  # 20-point lag
       composite_hand(canvas, hand_overlay, hand_pos)
   ```

3. **Hand Overlay Compositing**
   - Hand PNG with alpha channel (transparency)
   - Positioned at drawing location with 20-point lag
   - Alpha blending formula:
     ```
     output = alpha * hand + (1 - alpha) * canvas
     ```
   - Creates realistic "hand following pencil" effect

**Key Parameters:**
- `fps = 30`: Smooth motion (industry standard)
- `lag = 20 points`: Hand slightly behind stroke tip
- `stroke_width = 1px`: Fine pencil line

**Output:** List of BGR frames (numpy arrays)

---

## Stage 4: Video Export (video_exporter.py)

### FFmpeg Encoding

**Purpose:** Convert frames to compressed video file

**MP4 Export Process:**

1. **Frame Writing**
   ```python
   for idx, frame in enumerate(frames):
       cv2.imwrite(f"temp/frame_{idx:05d}.png", frame)
   ```

2. **FFmpeg Command**
   ```bash
   ffmpeg -y \
     -framerate 30 \
     -i temp/frame_%05d.png \
     -c:v libx264 \           # H.264 codec (universal)
     -preset medium \         # Encoding speed/quality tradeoff
     -crf 23 \                # Quality (18=high, 28=low)
     -pix_fmt yuv420p \       # Color format (compatible)
     -movflags +faststart \   # Enable web streaming
     output.mp4
   ```

**GIF Export (Optimized):**

1. **Palette Generation** (better quality than direct conversion)
   ```bash
   ffmpeg -i frames \
     -vf palettegen=stats_mode=diff \
     palette.png
   ```

2. **GIF Creation with Palette**
   ```bash
   ffmpeg -i frames -i palette.png \
     -lavfi paletteuse=dither=bayer:bayer_scale=5 \
     output.gif
   ```

**Quality Settings:**
- CRF 23: Good quality, moderate size (~2-5MB for 10s)
- CRF 18: High quality, larger size (~5-10MB)
- CRF 28: Lower quality, smaller size (~1-2MB)

---

## Performance Characteristics

### Complexity Analysis

| Stage | Time Complexity | Bottleneck |
|-------|----------------|------------|
| Edge Detection | O(W×H) | Canny algorithm |
| Contour Finding | O(W×H) | Connected components |
| Frame Generation | O(F×P) | Drawing points |
| Video Encoding | O(F×W×H) | FFmpeg compression |

Where:
- W, H = image dimensions
- F = number of frames
- P = number of drawing points

### Typical Performance (4-core CPU)

| Resolution | Duration | Processing Time | Output Size |
|-----------|----------|-----------------|-------------|
| 1080p | 10s | 12-18s | 3-5 MB |
| 720p | 10s | 8-12s | 2-3 MB |
| 4K | 10s | 25-35s | 8-12 MB |

### Optimization Strategies

1. **Point Downsampling**
   - Limit to 10,000 points max
   - 60% faster with minimal quality loss

2. **Frame Skip** (future)
   - Generate every 2nd frame, interpolate rest
   - 2× speedup for longer videos

3. **GPU Acceleration** (Phase 2)
   - Use CUDA for OpenCV operations
   - 3-5× speedup on edge detection

4. **FFmpeg Hardware Encoding**
   ```bash
   -c:v h264_nvenc  # NVIDIA GPU
   -c:v h264_qsv    # Intel Quick Sync
   ```
   - 4-8× faster encoding

---

## Scalability Considerations

### Current MVP Limits (Single Instance)
- **Concurrent Jobs:** 5-10 (CPU-bound)
- **Max Image:** 10 MB, 4K resolution
- **Memory Usage:** ~500MB per job
- **Processing Time:** 10-30 seconds

### Horizontal Scaling (Phase 2)

```
Load Balancer
      ↓
┌─────┴─────┬─────┬─────┐
│  Worker 1 │  W2 │  W3 │
└───────────┴─────┴─────┘
```

**Architecture:**
1. **Job Queue** (Redis + Celery)
   - Decouple API from processing
   - Async job execution
   - Progress tracking

2. **Worker Pool**
   - Auto-scaling based on queue length
   - Each worker: 2-4GB RAM, 2 CPUs
   - Stateless (no session storage)

3. **Object Storage** (S3/GCS)
   - Store generated videos
   - CDN for fast downloads
   - Automatic cleanup after 24h

**Capacity Estimate:**
- 10 workers × 6 jobs/min = **60 videos/minute**
- ~86,000 videos/day
- At $0.10/worker-hour = **$24/day**

---

## Future AI Upgrade Path

### Replace OpenCV with Stable Diffusion

**Current (OpenCV):**
```python
edges = cv2.Canny(image, 50, 150)
```

**Future (AI Model):**
```python
edges = sketch_model.generate(
    image=image,
    style="hand_drawn_pencil",
    detail_level=0.7
)
```

**Benefits:**
- More artistic, less mechanical
- Respects semantic content (faces, objects)
- Style customization (pencil, charcoal, ink)

**Implementation:**
- Use ControlNet with sketch conditioning
- Or fine-tuned SDXL model
- ~3-5x slower, but better quality

---

## Security & Validation

### Input Validation Pipeline

1. **File Type** (magic numbers, not extensions)
   ```python
   magic_bytes = file[:8]
   if magic_bytes[:2] == b'\xff\xd8':  # JPEG
       return "image/jpeg"
   ```

2. **Size Limits**
   - 10 MB max (prevents DoS)
   - Enforced at API layer

3. **Resolution Limits**
   - 4K max (prevents memory exhaustion)
   - Checked after PIL decode

4. **Content Safety** (Phase 2)
   - NSFW detection model
   - Reject inappropriate content

---

## Monitoring & Observability

### Key Metrics to Track

1. **Processing Time** (p50, p95, p99)
   - Alert if p95 > 30s

2. **Error Rate**
   - Target < 2%
   - Break down by error type

3. **Queue Length** (if using Celery)
   - Auto-scale at > 20 jobs

4. **Temp Storage Usage**
   - Alert if > 80% full

**Tools:**
- Prometheus + Grafana for metrics
- Sentry for error tracking
- CloudWatch/Stackdriver for logs

---

This architecture document provides the technical depth needed to:
1. Understand the system design
2. Debug issues
3. Optimize performance
4. Plan future enhancements

**Remember:** Start simple, measure everything, optimize bottlenecks.
