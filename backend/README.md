# Pencil Draw Backend

FastAPI-based backend for generating hand-drawn sketch animations.

## Quick Start

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Server

```bash
# Development
uvicorn app.main:app --reload --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### POST /api/generate

Generate sketch animation video.

**Request:**
```json
{
  "image": "base64_encoded_string",
  "duration": 10,
  "hand_style": "light_pencil",
  "output_format": "mp4"
}
```

**Response:**
```json
{
  "status": "success",
  "video_url": "/api/download/abc123.mp4",
  "file_id": "abc123",
  "duration_actual": 10.04,
  "frames_generated": 300,
  "file_size_mb": 2.5
}
```

### GET /api/download/{file_name}

Download generated video file.

### GET /api/health

Health check endpoint.

## Environment Variables

Create a `.env` file:

```bash
# API Settings
DEBUG=false
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# File Limits
MAX_IMAGE_SIZE_MB=10
MAX_RESOLUTION=4096

# Video Settings
DEFAULT_FPS=30
MIN_DURATION=1
MAX_DURATION=20

# Temp File Management
TEMP_DIR=temp
TEMP_FILE_RETENTION_HOURS=1
```

## Architecture

```
app/
├── main.py              # FastAPI app initialization
├── api/
│   ├── routes.py        # Endpoint handlers
│   └── models.py        # Pydantic schemas
├── core/
│   ├── config.py        # Settings management
│   ├── sketch_engine.py # Edge detection
│   ├── frame_generator.py # Frame creation
│   └── video_exporter.py # FFmpeg wrapper
└── utils/
    ├── validators.py    # Input validation
    └── file_manager.py  # Temp file cleanup
```

## Testing

```bash
# Install test dependencies
pip install pytest httpx

# Run tests
pytest tests/
```

## Production Deployment

### Docker

```bash
docker build -t pencil-draw-backend .
docker run -p 8000:8000 pencil-draw-backend
```

### Requirements

- Python 3.11+
- FFmpeg installed on system
- 2GB+ RAM per worker
- 1+ CPU cores
