from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
import sys
import os

# Add src to Python path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

# Import new architecture components
from src.controllers.standings import router as standings_router
from src.controllers.schedule import router as schedule_router
from src.controllers.race_results import router as race_results_router
from src.repositories.cache import cache_repo

app = FastAPI(
    title="F1 Dashboard API",
    description="Formula 1 Dashboard API",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include controllers with API prefix
app.include_router(standings_router, prefix="/api")
app.include_router(schedule_router, prefix="/api")
app.include_router(race_results_router, prefix="/api")

# Management APIs - keep these for future development
@app.get("/api/clear-cache")
def clear_cache():
    try:
        total_cleared = 0
        total_cleared += cache_repo.delete_pattern("driver_standings_*")
        total_cleared += cache_repo.delete_pattern("constructor_standings_*")
        total_cleared += cache_repo.delete_pattern("race_schedule_*")
        total_cleared += cache_repo.delete_pattern("race_results_*")
        total_cleared += cache_repo.delete_pattern("race_qualifying_*")
        total_cleared += cache_repo.delete_pattern("race_practice_*")
        total_cleared += cache_repo.delete_pattern("race_summary_*")
        total_cleared += cache_repo.delete_pattern("race_highlights_*")
        
        # Clear individual keys
        other_keys = ["available_years"]
        for key in other_keys:
            if cache_repo.exists(key):
                cache_repo.delete(key)
                total_cleared += 1
        
        return {"message": f"Cleared {total_cleared} cache entries"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cache-stats")
def cache_stats():
    try:
        stats = {
            "driver_standings": len(cache_repo.keys("driver_standings_*")),
            "constructor_standings": len(cache_repo.keys("constructor_standings_*")),
            "race_schedule": len(cache_repo.keys("race_schedule_*")),
            "race_results": len(cache_repo.keys("race_results_*")),
            "qualifying_results": len(cache_repo.keys("race_qualifying_*")),
            "practice_results": len(cache_repo.keys("race_practice_*")),
            "race_summary": len(cache_repo.keys("race_summary_*")),
            "race_highlights": len(cache_repo.keys("race_highlights_*")),
            "other": len([k for k in cache_repo.keys("available_years*")])
        }
        stats["total"] = sum(stats.values())
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {
        "message": "F1 Dashboard API",
        "version": "2.0.0",
        "docs": "/docs",
        "architecture": "Controller-Service-Repository"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 