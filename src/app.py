"""FastAPI application for Trading Journal."""

from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database.db_manager import DatabaseManager
from api.trades import router as trades_router
from api.journal import router as journal_router
from api.analytics import router as analytics_router
from api.trading212 import router as trading212_router
from api.overnight import router as overnight_router
from api.expenses import router as expenses_router
from api.settings import router as settings_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup and cleanup on shutdown."""
    # Startup: Initialize database
    db = DatabaseManager()
    # Database initialization happens automatically in DatabaseManager
    yield
    # Shutdown: Cleanup if needed


# Create FastAPI app
app = FastAPI(
    title="Trading Journal API",
    description="API for tracking trades and maintaining a trading journal with performance analytics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative dev port
        # Add production URL here when deployed
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers with /api prefix
app.include_router(trades_router, prefix="/api")
app.include_router(journal_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(trading212_router, prefix="/api")
app.include_router(overnight_router, prefix="/api")
app.include_router(expenses_router, prefix="/api")
app.include_router(settings_router, prefix="/api")

# Mount static files for production (frontend build)
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# SPA fallback - serve index.html for all non-API routes
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Serve the Vue.js SPA for all non-API routes."""
    index_file = frontend_dist / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "Frontend not built. Run 'npm run build' in frontend directory."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
