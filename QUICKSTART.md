# Pencil Draw - Getting Started

## Prerequisites

- **Docker & Docker Compose** (recommended)
- OR:
  - Python 3.11+
  - Node.js 18+
  - FFmpeg installed

## Quick Start with Docker (Easiest)

### 1. Clone & Configure

```bash
cd Pencil_Draw

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
```

### 2. Start Services

```bash
docker-compose up --build
```

### 3. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

That's it! 🎉

---

## Manual Setup (Without Docker)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local

# Run development server
npm run dev
```

---

## Testing the Application

1. Open http://localhost:3000
2. Upload an image (drag & drop or click to select)
3. Set duration (1-20 seconds)
4. Choose hand style
5. Select output format (MP4 or GIF)
6. Click "Generate Sketch Animation"
7. Wait 10-30 seconds
8. Download your video!

---

## Troubleshooting

### "FFmpeg not found"
Install FFmpeg:
- **Windows**: `choco install ffmpeg` or download from ffmpeg.org
- **Mac**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`

### Port already in use
Change ports in docker-compose.yml:
```yaml
ports:
  - "8001:8000"  # Backend
  - "3001:3000"  # Frontend
```

### Large image processing fails
Increase limits in `backend/.env`:
```bash
MAX_IMAGE_SIZE_MB=20
MAX_RESOLUTION=8192
```

---

## Production Deployment

### Environment Variables

**Backend (.env):**
```bash
DEBUG=false
ALLOWED_ORIGINS=https://yourdomain.com
MAX_IMAGE_SIZE_MB=10
```

**Frontend (.env.local):**
```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

### Deploy with Docker

```bash
# Build images
docker-compose build

# Push to registry
docker tag pencil-draw-backend your-registry/pencil-draw-backend:latest
docker push your-registry/pencil-draw-backend:latest

docker tag pencil-draw-frontend your-registry/pencil-draw-frontend:latest
docker push your-registry/pencil-draw-frontend:latest
```

### Cloud Deployment Options

1. **AWS ECS/Fargate** - Easy container deployment
2. **Google Cloud Run** - Serverless containers
3. **Azure Container Instances** - Simple container hosting
4. **DigitalOcean App Platform** - Simplified deployment
5. **Vercel (Frontend) + Railway (Backend)** - Quick setup

---

## Next Steps

- [ ] Add user authentication
- [ ] Implement job queue (Celery + Redis)
- [ ] Add more hand styles
- [ ] Integrate AI sketch models
- [ ] Create Canva app integration
- [ ] Add payment system (Stripe)

---

## Support

For issues or questions:
1. Check the documentation in `/backend/README.md` and `/frontend/README.md`
2. Review API docs at http://localhost:8000/docs
3. Open an issue on GitHub

---

**Built with ❤️ for creators**
