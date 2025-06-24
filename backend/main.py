from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any

# 导入业务逻辑函数
from standings_api import get_driver_standings, get_constructor_standings
from schedule_api import get_available_years, get_race_schedule, get_next_race_info, get_race_weekend_schedule, get_circuit_info
from backend.race_results_api_old import get_race_results, get_qualifying_results, get_practice_results, get_race_summary, get_race_highlights
from cache_utils import clear_cache_pattern, redis_client

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

# 积分榜API
@app.get("/api/driver-standings")
def driver_standings(year: Optional[int] = Query(None), round: Optional[int] = Query(None)):
    try:
        return get_driver_standings(year, round)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/constructor-standings")
def constructor_standings(year: Optional[int] = Query(None), round: Optional[int] = Query(None)):
    try:
        return get_constructor_standings(year, round)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 赛程API
@app.get("/api/available-years")
def available_years():
    try:
        return get_available_years()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/race-schedule")
def race_schedule(year: Optional[int] = Query(None)):
    try:
        return get_race_schedule(year)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/next-race")
def next_race(year: Optional[int] = Query(None)):
    try:
        return get_next_race_info(year)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/race-weekend-schedule")
def race_weekend_schedule(year: Optional[int] = Query(None), round: Optional[int] = Query(None)):
    try:
        return get_race_weekend_schedule(year, round)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/circuit-info")
def circuit_info(year: Optional[int] = Query(None), round: Optional[int] = Query(None)):
    try:
        return get_circuit_info(year, round)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 比赛结果API
@app.get("/api/race-results")
def race_results(year: int = Query(...), round: int = Query(...)):
    try:
        return get_race_results(year, round)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/qualifying-results")
def qualifying_results(year: int = Query(...), round: int = Query(...)):
    try:
        return get_qualifying_results(year, round)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/practice-results")
def practice_results(
    year: int = Query(...), 
    round: int = Query(...), 
    session: str = Query("FP1")
):
    try:
        return get_practice_results(year, round, session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/race-summary")
def race_summary(year: int = Query(...), round: int = Query(...)):
    try:
        return get_race_summary(year, round)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/race-highlights")
def race_highlights(year: int = Query(...), round: int = Query(...)):
    try:
        return get_race_highlights(year, round)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 管理API
@app.get("/api/clear-cache")
def clear_cache():
    try:
        total_cleared = 0
        total_cleared += clear_cache_pattern("driver_standings_*")
        total_cleared += clear_cache_pattern("constructor_standings_*")
        total_cleared += clear_cache_pattern("race_schedule_*")
        total_cleared += clear_cache_pattern("race_results_*")
        total_cleared += clear_cache_pattern("race_qualifying_*")
        total_cleared += clear_cache_pattern("race_practice_*")
        total_cleared += clear_cache_pattern("race_summary_*")
        total_cleared += clear_cache_pattern("race_highlights_*")
        
        # 清除单个键
        other_keys = ["available_years"]
        if redis_client.exists(*other_keys):
            redis_client.delete(*other_keys)
            total_cleared += len(other_keys)
        
        return {"message": f"已清除 {total_cleared} 个缓存条目"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cache-stats")
def cache_stats():
    try:
        stats = {
            "driver_standings": len(redis_client.keys("driver_standings_*")),
            "constructor_standings": len(redis_client.keys("constructor_standings_*")),
            "race_schedule": len(redis_client.keys("race_schedule_*")),
            "race_results": len(redis_client.keys("race_results_*")),
            "qualifying_results": len(redis_client.keys("race_qualifying_*")),
            "practice_results": len(redis_client.keys("race_practice_*")),
            "race_summary": len(redis_client.keys("race_summary_*")),
            "race_highlights": len(redis_client.keys("race_highlights_*")),
            "other": len(redis_client.keys("available_years"))
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
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 