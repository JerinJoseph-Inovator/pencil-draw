# ✏️ Pencil Draw

Transform images into hand-drawn sketch animations with realistic pencil drawing effects.

## 🚀 Quick Start (For Users)

### Step 1: Download the Backend
Download `PencilDraw.exe` from [Releases](https://github.com/JerinJoseph-Inovator/pencil-draw/releases)

### Step 2: Start the Server
Double-click `PencilDraw.exe` - a console window will appear showing the server is running.

### Step 3: Open the Web App
Go to: **https://jerinjoseph-inovator.github.io/pencil-draw**

### Step 4: Create Your Animation!
1. Upload an image
2. Choose duration (1-20 seconds)
3. Select hand style and drawing options
4. Click Generate!

---

## 🎯 Features

- **Drawing Directions**: Left→Right, Right→Left, Top→Bottom, Bottom→Top, Center-Out, Element-by-Element
- **Element Detection**: Auto-detects objects and draws them one by one
- **Organization Modes**: Default (top/bottom halves), Row-wise (5 rows), Column-wise (5 columns)
- **Hand Styles**: 4 custom hand overlays
- **Drawing Modes**: Normal, Outline Only, Outline + Fill
- **Output**: MP4 or GIF

---

## 🔒 Privacy First

✅ **100% Local Processing** - Images never leave your computer  
✅ **No Cloud Upload** - All processing happens on your machine  
✅ **No Account Required** - No sign-up, no tracking

---

## 🛠️ For Developers

### Prerequisites
- Python 3.10+
- Node.js 18+
- FFmpeg (for video export)

### Backend Setup
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
python server.py  # Runs on http://127.0.0.1:8123
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev  # Development
npm run build  # Production build
```

### Build Executable
```bash
cd backend
pip install pyinstaller
pyinstaller build.spec --clean
# Output: dist/PencilDraw.exe
```

---

## 📁 Project Structure

```
pencil-draw/
├── backend/
│   ├── app/
│   │   ├── api/          # Routes, models
│   │   ├── core/         # Frame generation, video export
│   │   └── utils/        # Validators
│   ├── assets/hands/     # Hand images
│   ├── server.py         # Standalone server
│   └── build.spec        # PyInstaller config
├── frontend/
│   ├── app/              # Next.js pages
│   ├── components/       # React components
│   └── lib/              # API client
└── .github/workflows/    # Auto-deploy to GitHub Pages
```

---

## 📜 License

MIT License
