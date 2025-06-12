from datetime import datetime
from typing import List, Dict, Any, Optional
import requests
from cache_utils import get_cache, set_cache, get_cache_expiry_seconds

def get_driver_standings(year: int = None) -> List[Dict[str, Any]]:
    """获取车手积分榜"""
    if year is None:
        year = datetime.now().year

    # 检查Redis缓存
    cache_key = f"driver_standings_{year}"
    cached_data = get_cache(cache_key)
    
    if cached_data:
        return cached_data

    try:
        # 使用 Jolpica-F1 API (Ergast 继承者)
        url = f"https://api.jolpi.ca/ergast/f1/{year}/driverStandings.json"
        response = requests.get(url)
        
        if response.status_code != 200:
            raise Exception(f"Failed to fetch driver standings for {year}")
        
        data_json = response.json()
        standings_list = data_json.get('MRData', {}).get('StandingsTable', {}).get('StandingsLists', [])
        
        if not standings_list:
            raise Exception(f"No driver standings data available for {year}")
        
        driver_standings = standings_list[0].get('DriverStandings', [])
        
        # 只取前十名
        driver_standings = driver_standings[:10]
        
        data = []
        for standing in driver_standings:
            driver = standing.get('Driver', {})
            data.append({
                "pos": int(standing.get('position', 0)),
                "name": f"{driver.get('givenName', '')} {driver.get('familyName', '')}",
                "points": float(standing.get('points', 0)),
                "evo": 0  # 可以自定义
            })
        
        # 缓存到下一场比赛
        cache_seconds = get_cache_expiry_seconds(year)
        set_cache(cache_key, data, cache_seconds)
        
        return data
        
    except Exception as e:
        raise Exception(f"Driver standings error: {str(e)}")

def get_constructor_standings(year: int = None) -> List[Dict[str, Any]]:
    """获取车队积分榜"""
    if year is None:
        year = datetime.now().year
    
    # 检查Redis缓存
    cache_key = f"constructor_standings_{year}"
    cached_data = get_cache(cache_key)
    
    if cached_data:
        return cached_data
    
    try:
        # 使用 Jolpica-F1 API (Ergast 继承者)
        url = f"https://api.jolpi.ca/ergast/f1/{year}/constructorStandings.json"
        response = requests.get(url)
        
        if response.status_code != 200:
            raise Exception(f"Failed to fetch constructor standings for {year}")
        
        data_json = response.json()
        standings_list = data_json.get('MRData', {}).get('StandingsTable', {}).get('StandingsLists', [])
        
        if not standings_list:
            raise Exception(f"No constructor standings data available for {year}")
        
        constructor_standings = standings_list[0].get('ConstructorStandings', [])
        
        # 只取前十名
        constructor_standings = constructor_standings[:10]
        
        data = []
        for standing in constructor_standings:
            constructor = standing.get('Constructor', {})
            data.append({
                "pos": int(standing.get('position', 0)),
                "name": constructor.get('name', ''),
                "points": float(standing.get('points', 0)),
                "evo": 0
            })
        
        # 缓存到下一场比赛
        cache_seconds = get_cache_expiry_seconds(year)
        set_cache(cache_key, data, cache_seconds)
        
        return data
        
    except Exception as e:
        raise Exception(f"Constructor standings error: {str(e)}") 