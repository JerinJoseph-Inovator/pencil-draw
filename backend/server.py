#!/usr/bin/env python3
"""
Pencil Draw - Standalone Server
================================
A production-ready FastAPI server that can be packaged as an executable.

Usage:
  - Direct: python server.py
  - Executable: double-click PencilDraw.exe

Author: Pencil Draw Team
"""
import os
import sys
import signal
import logging
import uvicorn
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("PencilDraw")

# Determine base path (works for both dev and PyInstaller)
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    BASE_DIR = Path(sys._MEIPASS)
    APP_DIR = Path(os.path.dirname(sys.executable))
else:
    # Running as script
    BASE_DIR = Path(__file__).parent
    APP_DIR = BASE_DIR

# Add app to path
sys.path.insert(0, str(BASE_DIR))

# Server configuration
HOST = "127.0.0.1"
PORT = 8123
ALLOWED_ORIGINS = [
    "https://jerinjoseph-inovator.github.io",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


def create_app():
    """Create and configure the FastAPI application."""
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
    
    # Import routes
    from app.api.routes import router
    from app.core.config import settings
    
    app = FastAPI(
        title="Pencil Draw API",
        description="Transform images into hand-drawn sketch animations",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # CORS middleware - explicit origins, no cookies
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=False,  # No cookies for security
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Accept"],
        expose_headers=["Content-Disposition"],
        max_age=3600,
    )
    
    # Include API routes
    app.include_router(router, prefix="/api")
    
    # Mount static files for hand assets
    hands_dir = BASE_DIR / "assets" / "hands"
    if hands_dir.exists():
        app.mount("/assets/hands", StaticFiles(directory=str(hands_dir)), name="hands")
    
    # Health endpoint
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "service": "Pencil Draw API",
            "version": "1.0.0",
            "port": PORT
        }
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "Pencil Draw API is running",
            "docs": f"http://{HOST}:{PORT}/docs",
            "health": f"http://{HOST}:{PORT}/health"
        }
    
    return app


def print_banner():
    """Print startup banner."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ✏️  PENCIL DRAW - Hand-Drawn Animation Generator           ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║   Server starting...                                         ║
║                                                              ║
║   Local URL:    http://127.0.0.1:8123                        ║
║   API Docs:     http://127.0.0.1:8123/docs                   ║
║   Health:       http://127.0.0.1:8123/health                 ║
║                                                              ║
║   Allowed Origins:                                           ║
║   • https://jerinjoseph-inovator.github.io                   ║
║   • http://localhost:3000                                    ║
║                                                              ║
║   Press Ctrl+C to stop the server                            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def graceful_shutdown(signum, frame):
    """Handle graceful shutdown."""
    logger.info("Shutdown signal received. Cleaning up...")
    logger.info("Server stopped gracefully. Goodbye! 👋")
    sys.exit(0)


def main():
    """Main entry point."""
    # Register signal handlers
    signal.signal(signal.SIGINT, graceful_shutdown)
    signal.signal(signal.SIGTERM, graceful_shutdown)
    
    # Print banner
    print_banner()
    
    # Create output directory for generated videos
    output_dir = APP_DIR / "output"
    output_dir.mkdir(exist_ok=True)
    logger.info(f"Output directory: {output_dir}")
    
    # Create and run app
    try:
        app = create_app()
        logger.info(f"Starting server on http://{HOST}:{PORT}")
        
        uvicorn.run(
            app,
            host=HOST,
            port=PORT,
            log_level="info",
            access_log=True,
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
