"""
FastAPI application entry point.
"""
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.routes import router
from app.core.config import settings


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description="Generate hand-drawn sketch animations from images",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Serve hand images as static files
    hands_dir = Path(__file__).parent.parent / "assets" / "hands"
    if hands_dir.exists():
        app.mount("/assets/hands", StaticFiles(directory=str(hands_dir)), name="hands")
    
    # Include API routes
    app.include_router(router, prefix="/api")
    
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "Pencil Draw API",
            "version": settings.version,
            "docs": "/docs"
        }
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
