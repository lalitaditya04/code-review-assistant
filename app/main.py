"""
Main FastAPI application
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from app.config import settings
from app.database import init_db
from app.routers import review, evaluation

# Initialize application
app = FastAPI(
    title=settings.APP_NAME,
    description="Automated code review with pre-analysis + AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware (for frontend development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates
templates_dir = Path(__file__).parent.parent / "templates"
templates_dir.mkdir(exist_ok=True)
templates = Jinja2Templates(directory=str(templates_dir))

# Include routers
app.include_router(review.router)
app.include_router(evaluation.router)


@app.on_event("startup")
async def startup_event():
    """
    Initialize application on startup.
    """
    print(f"\n{'='*60}")
    print(f"Starting {settings.APP_NAME}")
    print(f"{'='*60}")
    
    # Initialize directories
    settings.initialize()
    print(f"✅ Directories initialized")
    
    # Initialize database
    init_db()
    
    # Check API key
    if settings.validate_api_key():
        print(f"✅ AI Provider: {settings.AI_PROVIDER} (Model: {settings.AI_MODEL})")
    else:
        print(f"⚠️  WARNING: No valid API key configured!")
        print(f"   Please set {settings.AI_PROVIDER.upper()}_API_KEY in your .env file")
    
    print(f"{'='*60}\n")


@app.get("/")
async def home(request: Request):
    """
    Serve the dashboard homepage.
    """
    return templates.TemplateResponse(
        "dashboard.html", 
        {
            "request": request,
            "app_name": settings.APP_NAME,
            "ai_provider": settings.AI_PROVIDER,
            "api_configured": settings.validate_api_key()
        }
    )


@app.get("/api")
async def api_root():
    """
    API root - information about the API.
    """
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "ai_provider": settings.AI_PROVIDER,
        "ai_model": settings.AI_MODEL,
        "api_key_configured": settings.validate_api_key(),
        "endpoints": {
            "upload_review": "POST /api/review",
            "quick_scan": "POST /api/review/quick",
            "get_review": "GET /api/review/{id}",
            "list_reviews": "GET /api/reviews",
            "delete_review": "DELETE /api/review/{id}",
            "statistics": "GET /api/stats",
            "health": "GET /api/health",
            "evaluation_benchmark": "GET /api/evaluation/benchmark",
            "evaluation_report": "GET /api/evaluation/benchmark/report",
            "evaluation_metrics": "GET /api/evaluation/metrics"
        }
    }


if __name__ == "__main__":
    import uvicorn
    import multiprocessing
    
    # Fix for Windows multiprocessing
    multiprocessing.freeze_support()
    
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=settings.DEBUG,
        reload_excludes=["*.db", "*.sqlite", "*.sqlite3"]
    )
