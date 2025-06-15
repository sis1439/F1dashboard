from datetime import datetime
from typing import List, Dict, Any, Optional
import requests
from cache_utils import get_cache, set_cache, get_cache_expiry_seconds

def get_latest_round(year: int) -> int:
    """获取指定年份的最新轮次"""
    try:
        url = f"https://api.jolpi.ca/ergast/f1/{year}/driverStandings.json"
        response = requests.get(url)
        data_json = response.json()
        standings_list = data_json.get('MRData', {}).get('StandingsTable', {}).get('StandingsLists', [])
        if standings_list:
            return int(standings_list[0].get('round', 1))
        return 1
    except:
        return 1

def get_driver_standings(year: int = None, round: int = None) -> List[Dict[str, Any]]:
    """获取车手积分榜，支持排名变化（evo）和积分变化（points_change）"""
    if year is None:
        year = datetime.now().year

    # 如果没有指定round，获取最新轮次
    if round is None:
        round = get_latest_round(year)

    # 构造缓存key
    cache_key = f"driver_standings_{year}_{round}"
    cached_data = get_cache(cache_key)
    if cached_data:
        return cached_data

    # 获取当前场次积分榜
    url = f"https://api.jolpi.ca/ergast/f1/{year}/{round}/driverStandings.json"
    response = requests.get(url)
    data_json = response.json()
    standings_list = data_json.get('MRData', {}).get('StandingsTable', {}).get('StandingsLists', [])
    if not standings_list:
        return []
    driver_standings = standings_list[0].get('DriverStandings', [])[:10]

    # 获取上一场积分榜和排名
    prev_points = {}
    prev_positions = {}
    if round > 1:
        prev_url = f"https://api.jolpi.ca/ergast/f1/{year}/{round-1}/driverStandings.json"
        prev_response = requests.get(prev_url)
        if prev_response.status_code == 200:
            prev_json = prev_response.json()
            prev_list = prev_json.get('MRData', {}).get('StandingsTable', {}).get('StandingsLists', [])
            if prev_list:
                prev_standings = prev_list[0].get('DriverStandings', [])
                prev_points = {s['Driver']['driverId']: float(s['points']) for s in prev_standings}
                prev_positions = {s['Driver']['driverId']: int(s['position']) for s in prev_standings}

    data = []
    for standing in driver_standings:
        driver = standing.get('Driver', {})
        driver_id = driver.get('driverId', '')
        current_points = float(standing.get('points', 0))
        current_position = int(standing.get('position', 0))
        
        # 计算积分变化
        prev_point = prev_points.get(driver_id, 0)
        points_change = current_points - prev_point
        
        # 计算排名变化（上一场排名 - 当前排名，正数表示排名上升）
        prev_position = prev_positions.get(driver_id, current_position)
        evo = prev_position - current_position
        
        data.append({
            "pos": current_position,
            "name": f"{driver.get('givenName', '')} {driver.get('familyName', '')}",
            "points": current_points,
            "points_change": points_change,
            "evo": evo
        })
    
    # 缓存到下一场比赛
    cache_seconds = get_cache_expiry_seconds(year)
    set_cache(cache_key, data, cache_seconds)
    return data

def get_constructor_standings(year: int = None, round: int = None) -> List[Dict[str, Any]]:
    """获取车队积分榜，支持排名变化（evo）和积分变化（points_change）"""
    if year is None:
        year = datetime.now().year

    # 如果没有指定round，获取最新轮次
    if round is None:
        round = get_latest_round(year)

    cache_key = f"constructor_standings_{year}_{round}"
    cached_data = get_cache(cache_key)
    if cached_data:
        return cached_data

    # 获取当前场次积分榜
    url = f"https://api.jolpi.ca/ergast/f1/{year}/{round}/constructorStandings.json"
    response = requests.get(url)
    data_json = response.json()
    standings_list = data_json.get('MRData', {}).get('StandingsTable', {}).get('StandingsLists', [])
    if not standings_list:
        return []
    constructor_standings = standings_list[0].get('ConstructorStandings', [])[:10]

    # 获取上一场积分榜和排名
    prev_points = {}
    prev_positions = {}
    if round > 1:
        prev_url = f"https://api.jolpi.ca/ergast/f1/{year}/{round-1}/constructorStandings.json"
        prev_response = requests.get(prev_url)
        if prev_response.status_code == 200:
            prev_json = prev_response.json()
            prev_list = prev_json.get('MRData', {}).get('StandingsTable', {}).get('StandingsLists', [])
            if prev_list:
                prev_standings = prev_list[0].get('ConstructorStandings', [])
                prev_points = {s['Constructor']['constructorId']: float(s['points']) for s in prev_standings}
                prev_positions = {s['Constructor']['constructorId']: int(s['position']) for s in prev_standings}

    data = []
    for standing in constructor_standings:
        constructor = standing.get('Constructor', {})
        constructor_id = constructor.get('constructorId', '')
        current_points = float(standing.get('points', 0))
        current_position = int(standing.get('position', 0))
        
        # 计算积分变化
        prev_point = prev_points.get(constructor_id, 0)
        points_change = current_points - prev_point
        
        # 计算排名变化（上一场排名 - 当前排名，正数表示排名上升）
        prev_position = prev_positions.get(constructor_id, current_position)
        evo = prev_position - current_position
        
        data.append({
            "pos": current_position,
            "name": constructor.get('name', ''),
            "points": current_points,
            "points_change": points_change,
            "evo": evo
        })
    
    cache_seconds = get_cache_expiry_seconds(year)
    set_cache(cache_key, data, cache_seconds)
    return data 