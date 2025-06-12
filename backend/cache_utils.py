import redis
import json
from datetime import datetime, timedelta
from typing import Any, Optional
import pandas as pd
import fastf1

# Redis连接
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def get_cache(key: str) -> Optional[Any]:
    """获取缓存数据"""
    cached_data = redis_client.get(key)
    if cached_data:
        return json.loads(cached_data)
    return None

def set_cache(key: str, data: Any, expiry_seconds: int):
    """设置缓存数据"""
    redis_client.setex(key, expiry_seconds, json.dumps(data))

def clear_cache_pattern(pattern: str):
    """根据模式清除缓存"""
    keys = redis_client.keys(pattern)
    if keys:
        redis_client.delete(*keys)
        return len(keys)
    return 0

def get_next_race_date(year: int = None):
    """获取下一场比赛日期用于智能缓存过期"""
    if year is None:
        year = datetime.now().year
    
    try:
        schedule = fastf1.get_event_schedule(year)
        now = datetime.now()
        
        # 找到下一场比赛 (EventDate 在未来)
        future_races = schedule[pd.to_datetime(schedule['EventDate']) > now]
        
        if not future_races.empty:
            next_race_date = pd.to_datetime(future_races.iloc[0]['EventDate'])
            return next_race_date
        else:
            # 如果本年没有未来的比赛，缓存1周
            return now + timedelta(weeks=1)
    except:
        # 后备方案：缓存1周
        return datetime.now() + timedelta(weeks=1)

def get_cache_expiry_seconds(year: int = None):
    """计算缓存过期时间直到下一场比赛"""
    next_race = get_next_race_date(year)
    now = datetime.now()
    
    # 缓存到下一场比赛，但最少1小时，最多1周
    seconds_until_race = int((next_race - now).total_seconds())
    return max(3600, min(seconds_until_race, 604800))  # 1小时到1周 