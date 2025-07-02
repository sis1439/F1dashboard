from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys
import os

# Add src to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings
from controllers.standings import router as standings_router
from controllers.schedule import router as schedule_router
from controllers.race_results import router as race_results_router
# Import other routers as they are created
# from controllers.admin import router as admin_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format=settings.log_format,
    handlers=[
        logging.StreamHandler(sys.stdout),
        # Add file handler if needed
        # logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events"""
    
    # Startup
    logger.info("Starting F1 Dashboard API...")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Redis host: {settings.redis_host}:{settings.redis_port}")
    
    # Initialize FastF1 cache
    try:
        import fastf1
        fastf1.Cache.enable_cache(settings.fastf1_cache_dir)
        logger.info(f"FastF1 cache enabled at: {settings.fastf1_cache_dir}")
    except Exception as e:
        logger.error(f"Failed to initialize FastF1 cache: {e}")
    
    # Test cache connection
    try:
        from repositories.cache import cache_repo
        if cache_repo.redis_client:
            cache_repo.redis_client.ping()
            logger.info("Cache connection established")
        else:
            logger.warning("Cache connection not available - running without cache")
    except Exception as e:
        logger.warning(f"Cache connection test failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down F1 Dashboard API...")


# Create FastAPI application instance
app = FastAPI(
    title=settings.app_name,
    description="Formula 1 Dashboard API with refactored architecture",
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(standings_router, prefix=settings.api_prefix)
app.include_router(schedule_router, prefix=settings.api_prefix)
app.include_router(race_results_router, prefix=settings.api_prefix)
# Include other routers as they are created
# app.include_router(admin_router, prefix=settings.api_prefix)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return HTTPException(
        status_code=500,
        detail="Internal server error"
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test cache connection
        from repositories.cache import cache_repo
        cache_status = "connected" if cache_repo.redis_client else "disconnected"
        
        return {
            "status": "healthy",
            "version": settings.app_version,
            "cache": cache_status,
            "debug": settings.debug
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs" if settings.debug else "Documentation not available in production",
        "health": "/health"
    }


# For development server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=settings.debug,
        log_level=settings.log_level.lower()
    ) 