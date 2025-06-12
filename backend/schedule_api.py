from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd
import fastf1
from cache_utils import get_cache, set_cache

def get_available_years() -> List[int]:
    """获取可用年份"""
    # 检查Redis缓存
    cache_key = "available_years"
    cached_data = get_cache(cache_key)
    
    if cached_data:
        return cached_data
    
    # 从2023年到当前年份
    current_year = datetime.now().year
    years = list(range(2023, current_year + 1))
    
    # 缓存1周（年份不经常变化）
    set_cache(cache_key, years, int(timedelta(weeks=1).total_seconds()))
    
    return years

def get_race_schedule(year: int = None) -> List[Dict[str, Any]]:
    """获取完整的赛季赛程"""
    if year is None:
        year = datetime.now().year
    
    cache_key = f"race_schedule_{year}"
    cached_data = get_cache(cache_key)
    
    if cached_data:
        return cached_data
    
    try:
        schedule = fastf1.get_event_schedule(year)
        races = []
        
        for _, race in schedule.iterrows():
            races.append({
                "round": int(race['RoundNumber']),
                "race_name": race['EventName'],
                "location": race['Location'],
                "country": race['Country'],
                "date": race['EventDate'].strftime('%Y-%m-%d'),
                "format": race['EventFormat'] if 'EventFormat' in race else 'Conventional'
            })
        
        # 缓存1周（赛程很少变化）
        set_cache(cache_key, races, int(timedelta(weeks=1).total_seconds()))
        return races
        
    except Exception as e:
        raise Exception(f"Race schedule error: {str(e)}")

def get_next_race_info(year: int = None) -> Dict[str, Any]:
    """获取下一场比赛信息"""
    if year is None:
        year = datetime.now().year
    
    try:
        schedule = fastf1.get_event_schedule(year)
        now = datetime.now()
        
        future_races = schedule[pd.to_datetime(schedule['EventDate']) > now]
        
        if not future_races.empty:
            next_race = future_races.iloc[0]
            return {
                "race_name": next_race['EventName'],
                "date": next_race['EventDate'].strftime('%Y-%m-%d'),
                "location": next_race['Location'],
                "country": next_race['Country']
            }
        else:
            return {"message": "No upcoming races this year"}
    except Exception as e:
        raise Exception(f"Next race info error: {str(e)}") 