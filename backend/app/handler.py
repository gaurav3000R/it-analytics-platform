from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import uvicorn

from app.config import settings
from app.database import engine, Base
from app.api import projects, risks, analytics, ai_insights, bug_tracker, resource_utilization, cost_forecasting
from app.middleware import MonitoringMiddleware, metrics_endpoint
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting IT Analytics Platform...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")
    
    # Check Gemini API key
    if settings.GOOGLE_API_KEY:
        logger.info("Gemini AI integration enabled")
    else:
        logger.warning("Gemini AI integration disabled - GOOGLE_API_KEY not set")
    
    yield
    
    # Shutdown
    logger.info("Shutting down IT Analytics Platform...")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-Powered Early Warning System for IT Services Projects with Gemini AI Integration",
    lifespan=lifespan
)

# Add monitoring middleware
app.add_middleware(MonitoringMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(projects.router, prefix=settings.API_V1_STR)
app.include_router(risks.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)
app.include_router(ai_insights.router, prefix=settings.API_V1_STR)
app.include_router(bug_tracker.router, prefix=settings.API_V1_STR)
app.include_router(resource_utilization.router, prefix=settings.API_V1_STR)
app.include_router(cost_forecasting.router, prefix=settings.API_V1_STR)

# Monitoring endpoints
app.add_route("/metrics", metrics_endpoint)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "IT Analytics Platform API",
        "version": settings.VERSION,
        "status": "running",
        "features": {
            "risk_prediction": True,
            "anomaly_detection": True,
            "csv_data_loading": True,
            "gemini_ai_insights": bool(settings.GOOGLE_API_KEY),
            "cost_forecasting": True,
            "resource_utilization": True,
            "bug_tracking": True
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from app.middleware.monitoring import get_system_metrics
    
    # Test Gemini connection if API key is available
    gemini_status = "not_configured"
    if settings.GOOGLE_API_KEY:
        try:
            from app.utils.gemini_client import get_gemini_client
            client = get_gemini_client()
            gemini_status = "connected"
        except Exception as e:
            gemini_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "system_metrics": get_system_metrics(),
        "integrations": {
            "gemini_ai": gemini_status,
            "database": "connected"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.handler:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )