# 🧪 Testing Guide

## Manual Testing Checklist

### Backend Tests

#### 1. Health Check
```bash
curl http://localhost:8000/api/health
```
**Expected:** `{"status":"healthy","version":"1.0.0","temp_files_count":0}`

#### 2. API Documentation
Visit: http://localhost:8000/docs
- Verify Swagger UI loads
- Check all endpoints are documented
- Try "Try it out" feature

#### 3. Image Upload Validation
Test with Swagger UI or curl:

**Valid Image:**
```bash
# Convert test image to base64
$base64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes("test.jpg"))

# Send request (PowerShell)
$body = @{
    image = $base64
    duration = 10
    hand_style = "light_pencil"
    output_format = "mp4"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/generate" -Method POST -Body $body -ContentType "application/json"
```

**Expected:** Success response with video URL

**Invalid Cases to Test:**
- ❌ Image > 10MB → "IMAGE_SIZE_EXCEEDED"
- ❌ Invalid format → "UNSUPPORTED_FORMAT"
- ❌ Corrupted base64 → "INVALID_BASE64"
- ❌ Resolution > 4K → "RESOLUTION_EXCEEDED"

#### 4. Duration Validation
```json
{"duration": 0}     // ❌ "INVALID_DURATION"
{"duration": 21}    // ❌ "INVALID_DURATION"
{"duration": 10}    // ✅ Success
```

#### 5. Hand Style Validation
```json
{"hand_style": "invalid"}     // ❌ "Hand style must be one of..."
{"hand_style": "light_pencil"} // ✅ Success
```

#### 6. Video Download
After generation:
```bash
curl -O http://localhost:8000/api/download/abc123.mp4
```
**Expected:** MP4 file downloads successfully

---

### Frontend Tests

#### 1. Image Upload
- ✅ Drag & drop an image
- ✅ Click to select file
- ✅ Preview shows uploaded image
- ✅ Remove button appears on hover
- ❌ Try uploading .txt file → Should reject
- ❌ Try uploading 15MB image → Should show error

#### 2. Duration Slider
- ✅ Move slider from 1 to 20
- ✅ Value updates in real-time
- ✅ Disabled during generation

#### 3. Hand Style Selector
- ✅ Click different styles
- ✅ Selected style shows checkmark
- ✅ Disabled during generation

#### 4. Output Format
- ✅ Toggle between MP4 and GIF
- ✅ Selection persists during generation

#### 5. Generate Button
- ✅ Disabled when no image
- ✅ Shows loading state during generation
- ✅ Text changes to "Generating Animation..."

#### 6. Preview Area
- ✅ Shows placeholder before upload
- ✅ Shows uploaded image
- ✅ Shows loading spinner during generation
- ✅ Shows video player after completion
- ✅ Video autoplays and loops

#### 7. Download Button
- ✅ Appears after video generation
- ✅ Downloads file with correct name
- ✅ File plays in local video player

#### 8. Error Handling
Test these scenarios:
- ❌ Backend offline → "Failed to generate video"
- ❌ Invalid image → Shows error message
- ❌ Network timeout → Proper error display

#### 9. Responsive Design
Test on:
- ✅ Desktop (1920×1080)
- ✅ Tablet (768×1024)
- ✅ Mobile (375×667)

---

## Automated Testing (Future)

### Backend Unit Tests

Create `backend/tests/test_api.py`:

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_generate_invalid_duration():
    response = client.post("/api/generate", json={
        "image": "base64string",
        "duration": 0,
        "hand_style": "light_pencil",
        "output_format": "mp4"
    })
    assert response.status_code == 400
    assert "INVALID_DURATION" in response.json()["code"]
```

**Run:**
```bash
pytest backend/tests/
```

### Frontend E2E Tests

Create `frontend/tests/e2e.spec.ts` with Playwright:

```typescript
import { test, expect } from '@playwright/test'

test('complete generation flow', async ({ page }) => {
  await page.goto('http://localhost:3000')
  
  // Upload image
  await page.setInputFiles('input[type="file"]', 'test-image.jpg')
  
  // Set duration
  await page.locator('input[type="range"]').fill('5')
  
  // Select hand style
  await page.click('text=Light Pencil')
  
  // Generate
  await page.click('text=Generate Sketch Animation')
  
  // Wait for completion
  await expect(page.locator('video')).toBeVisible({ timeout: 60000 })
  
  // Download
  await page.click('text=Download Video')
})
```

**Run:**
```bash
npx playwright test
```

---

## Performance Testing

### Load Test with Apache Bench

```bash
# Generate 100 requests with 10 concurrent
ab -n 100 -c 10 -p request.json -T application/json http://localhost:8000/api/generate
```

**Metrics to Track:**
- Requests per second
- Mean response time
- 95th percentile latency
- Error rate

**Expected Results (Single Instance):**
- ~5-10 requests/min sustained
- Mean: 15-20s
- p95: 30s
- Error rate: < 2%

### Memory Usage

```bash
# Monitor backend memory
docker stats pencil-draw-backend
```

**Expected:** ~500MB per job, peaks at ~2GB with 5 concurrent

---

## Browser Compatibility

| Browser | Version | Status |
|---------|---------|--------|
| Chrome | 120+ | ✅ Full support |
| Firefox | 121+ | ✅ Full support |
| Safari | 17+ | ✅ Full support |
| Edge | 120+ | ✅ Full support |
| Mobile Safari | iOS 16+ | ✅ Full support |
| Chrome Mobile | Latest | ✅ Full support |

**Test on:**
- Windows 11
- macOS Sonoma
- iOS 17
- Android 13+

---

## Security Testing

### 1. File Upload Exploits
Try uploading:
- ❌ `.exe` disguised as `.jpg` → Should reject
- ❌ Malformed EXIF data → Should handle gracefully
- ❌ Zip bomb (large compressed) → Should hit size limit

### 2. Input Validation
```bash
# SQL injection attempt (should sanitize)
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"image":"'; DROP TABLE users;--","duration":10}'

# XSS attempt
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"image":"<script>alert(1)</script>","duration":10}'
```

**Expected:** Validation errors, no execution

### 3. Rate Limiting (Add in Phase 2)
```bash
# Spam requests
for i in {1..100}; do
  curl http://localhost:8000/api/generate &
done
```

**Current:** No rate limiting (add Redis-based limit later)

---

## Monitoring & Observability

### Logs to Check

**Backend logs:**
```bash
docker logs pencil-draw-backend -f
```

**Watch for:**
- ✅ Request timestamps
- ✅ Processing times
- ❌ Error tracebacks
- ❌ Memory warnings

**Frontend logs:**
```bash
docker logs pencil-draw-frontend -f
```

**Watch for:**
- ✅ Build success
- ✅ Route access logs
- ❌ 404 errors

### Temp File Cleanup

```bash
# Check temp directory
ls -lh backend/temp/

# Should auto-clean files > 1 hour old
```

---

## Common Issues & Solutions

### Issue: "FFmpeg not found"
**Solution:**
```bash
# Windows
choco install ffmpeg

# Mac
brew install ffmpeg

# Linux
sudo apt install ffmpeg

# Docker (already included in Dockerfile)
```

### Issue: "Module not found"
**Solution:**
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Issue: "CORS error"
**Solution:** Check `backend/.env`:
```bash
ALLOWED_ORIGINS=http://localhost:3000
```

### Issue: "Port already in use"
**Solution:**
```bash
# Find process on port
netstat -ano | findstr :8000

# Kill process
taskkill /PID <process_id> /F
```

### Issue: "Video not playing"
**Checklist:**
1. Check browser console for errors
2. Verify video URL is accessible
3. Check file was generated: `ls backend/temp/`
4. Try different browser

---

## Test Data

### Sample Images to Use

**Good Test Cases:**
- Simple line drawing (icon, logo)
- Portrait photo (high contrast)
- Landscape with clear subjects
- Text document (clean edges)

**Edge Cases:**
- Very dark image (low contrast)
- All white image (no edges)
- Blurry photo (soft edges)
- Gradient only (few edges)

**Download test images:**
```bash
# Create test directory
mkdir test-images

# Use sample images from:
# - Unsplash (free photos)
# - Wikimedia Commons
# - Your own photos
```

---

## Acceptance Criteria

### MVP Launch Checklist

#### Functionality
- [ ] Image upload works (drag & drop + picker)
- [ ] All 5 hand styles generate correctly
- [ ] Duration slider affects video length
- [ ] Both MP4 and GIF exports work
- [ ] Download delivers correct file
- [ ] Preview shows video properly

#### Performance
- [ ] 1080p image generates in < 20s
- [ ] No memory leaks after 10 generations
- [ ] Temp files auto-delete after 1 hour
- [ ] API responds to health checks

#### UX
- [ ] Loading states show during processing
- [ ] Errors display clearly to users
- [ ] Mobile layout is usable
- [ ] All text is readable (contrast)

#### Technical
- [ ] Docker Compose starts without errors
- [ ] API documentation is complete
- [ ] Code follows style guides
- [ ] README instructions work

---

## Regression Testing (After Updates)

When you change code, re-test:

**Backend changes:**
1. Health check
2. Generate with default params
3. Generate with all hand styles
4. Both output formats
5. Edge cases (large image, long duration)

**Frontend changes:**
1. Upload flow
2. All interactive controls
3. Mobile responsive layout
4. Download functionality

---

## Continuous Integration (Future)

### GitHub Actions Workflow

```yaml
name: CI

on: [push, pull_request]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: cd backend && pip install -r requirements.txt
      - run: cd backend && pytest

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: cd frontend && npm install
      - run: cd frontend && npm run build
```

---

**Testing is how you sleep well at night.** 😴

Ship with confidence!
