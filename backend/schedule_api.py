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

def get_race_weekend_schedule(year: int = None, round: int = None) -> Dict[str, Any]:
    """获取比赛周末的详细时间表，包括所有sessions"""
    if year is None:
        year = datetime.now().year
    
    # 如果没有指定round，获取下一场比赛
    if round is None:
        try:
            schedule = fastf1.get_event_schedule(year)
            now = datetime.now()
            # 转换为相同类型进行比较
            now_timestamp = pd.Timestamp(now.date())
            future_races = schedule[pd.to_datetime(schedule['EventDate']) >= now_timestamp]
            if not future_races.empty:
                next_race = future_races.iloc[0]
                round = int(next_race['RoundNumber'])
            else:
                # 如果本年没有未来比赛，获取最后一场比赛
                last_race = schedule.iloc[-1]
                round = int(last_race['RoundNumber'])
        except Exception as e:
            return {"error": f"Could not determine race round: {str(e)}"}
    
    cache_key = f"race_weekend_schedule_{year}_{round}"
    cached_data = get_cache(cache_key)
    
    if cached_data:
        return cached_data
    
    try:
        schedule = fastf1.get_event_schedule(year)
        race_info = schedule[schedule['RoundNumber'] == round].iloc[0]
        
        sessions = []
        
        # Session持续时间定义（分钟）
        session_durations = {
            'FP1': 90,  # Practice 1: 90分钟
            'FP2': 90,  # Practice 2: 90分钟  
            'FP3': 60,  # Practice 3: 60分钟
            'Q': 60,    # Qualifying: 60分钟
            'R': 120    # Race: 约2小时
        }
        
        # 直接使用schedule中的session时间信息
        session_mapping = {
            'Session1Date': {'name': 'Practice 1', 'code': 'FP1'},
            'Session2Date': {'name': 'Practice 2', 'code': 'FP2'},
            'Session3Date': {'name': 'Practice 3', 'code': 'FP3'},
            'Session4Date': {'name': 'Qualifying', 'code': 'Q'},
            'Session5Date': {'name': 'Race', 'code': 'R'}
        }
        
        current_time = datetime.now()
        
        for session_date_col, session_info in session_mapping.items():
            if session_date_col in race_info and pd.notna(race_info[session_date_col]):
                session_datetime = race_info[session_date_col]
                if isinstance(session_datetime, str):
                    session_datetime = pd.to_datetime(session_datetime)
                
                # 计算结束时间
                duration_minutes = session_durations.get(session_info['code'], 90)
                end_datetime = session_datetime + pd.Timedelta(minutes=duration_minutes)
                
                # 确定状态 - 需要考虑时区
                status = "upcoming"  # 默认即将开始
                
                # 转换为UTC进行比较
                if session_datetime.tz is not None:
                    # 如果session有时区信息，转换current_time为UTC
                    current_utc = pd.Timestamp.now(tz='UTC')
                    session_utc = session_datetime.tz_convert('UTC')
                    end_utc = end_datetime.tz_convert('UTC')
                    
                    if current_utc > end_utc:
                        status = "completed"
                    elif current_utc >= session_utc:
                        status = "live"
                else:
                    # 如果没有时区信息，使用本地时间比较
                    if current_time > end_datetime.to_pydatetime():
                        status = "completed"
                    elif current_time >= session_datetime.to_pydatetime():
                        status = "live"
                
                sessions.append({
                    "name": session_info['name'],
                    "code": session_info['code'],
                    "date": session_datetime.strftime('%Y-%m-%d'),
                    "time": session_datetime.strftime('%H:%M'),
                    "datetime": session_datetime.isoformat(),
                    "end_datetime": end_datetime.isoformat(),
                    "end_time": end_datetime.strftime('%H:%M'),
                    "status": status,
                    "duration_minutes": duration_minutes
                })
        
        race_data = {
            "race_info": {
                "round": int(race_info['RoundNumber']),
                "race_name": race_info['EventName'],
                "location": race_info['Location'],
                "country": race_info['Country'],
                "date": race_info['EventDate'].strftime('%Y-%m-%d'),
                "official_name": race_info.get('OfficialEventName', race_info['EventName'])
            },
            "sessions": sessions,
            "circuit": {
                "name": race_info.get('CircuitShortName', ''),
                "location": race_info['Location'],
                "country": race_info['Country']
            }
        }
        
        # 缓存1小时（比赛时间可能会有微调）
        set_cache(cache_key, race_data, 3600)
        return race_data
        
    except Exception as e:
        raise Exception(f"Race weekend schedule error: {str(e)}")

def get_circuit_info(year: int = None, round: int = None) -> Dict[str, Any]:
    """获取赛道信息，包括赛道图片URL等"""
    if year is None:
        year = datetime.now().year
    
    # 如果没有指定round，获取下一场比赛
    if round is None:
        try:
            schedule = fastf1.get_event_schedule(year)
            now = datetime.now()
            # 转换为相同类型进行比较
            now_timestamp = pd.Timestamp(now.date())
            future_races = schedule[pd.to_datetime(schedule['EventDate']) >= now_timestamp]
            if not future_races.empty:
                next_race = future_races.iloc[0]
                round = int(next_race['RoundNumber'])
            else:
                # 如果本年没有未来比赛，获取最后一场比赛
                last_race = schedule.iloc[-1]
                round = int(last_race['RoundNumber'])
        except Exception as e:
            return {"error": f"Could not determine race round: {str(e)}"}
    
    cache_key = f"circuit_info_{year}_{round}"
    cached_data = get_cache(cache_key)
    
    if cached_data:
        return cached_data
    
    try:
        schedule = fastf1.get_event_schedule(year)
        race_info = schedule[schedule['RoundNumber'] == round].iloc[0]
        
        # 基本赛道信息
        circuit_data = {
            "name": race_info.get('CircuitShortName', ''),
            "location": race_info['Location'],
            "country": race_info['Country'],
            "round": round,
            "race_name": race_info['EventName']
        }
        
        # 赛道图片URL映射（基于赛道名称）
        circuit_images = {
            "Bahrain": "https://www.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Bahrain_Circuit.png.transform/9col/image.png",
            "Saudi Arabia": "https://www.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Saudi_Arabia_Circuit.png.transform/9col/image.png",
            "Australia": "https://www.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Australia_Circuit.png.transform/9col/image.png",
            "Japan": "https://www.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Japan_Circuit.png.transform/9col/image.png",
            "China": "https://www.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/China_Circuit.png.transform/9col/image.png",
            "Miami": "https://www.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Miami_Circuit.png.transform/9col/image.png",
            "Emilia Romagna": "https://www.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Emilia_Romagna_Circuit.png.transform/9col/image.png",
            "Monaco": "https://www.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Monaco_Circuit.png.transform/9col/image.png",
            "Canada": "https://www.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Canada_Circuit.png.transform/9col/image.png",
            "Spain": "https://www.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Spain_Circuit.png.transform/9col/image.png",
            "Austria": "https://www.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Austria_Circuit.png.transform/9col/image.png",
            "Great Britain": "https://www.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Great_Britain_Circuit.png.transform/9col/image.png",
            "Hungary": "https://www.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Hungary_Circuit.png.transform/9col/image.png",
            "Belgium": "https://www.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Belgium_Circuit.png.transform/9col/image.png",
            "Netherlands": "https://www.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Netherlands_Circuit.png.transform/9col/image.png",
            "Italy": "https://www.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Italy_Circuit.png.transform/9col/image.png",
            "Azerbaijan": "https://www.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Azerbaijan_Circuit.png.transform/9col/image.png",
            "Singapore": "https://www.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Singapore_Circuit.png.transform/9col/image.png",
            "United States": "https://www.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/USA_Circuit.png.transform/9col/image.png",
            "Mexico": "https://www.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Mexico_Circuit.png.transform/9col/image.png",
            "Brazil": "https://www.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Brazil_Circuit.png.transform/9col/image.png",
            "Las Vegas": "https://www.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Las_Vegas_Circuit.png.transform/9col/image.png",
            "Qatar": "https://www.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Qatar_Circuit.png.transform/9col/image.png",
            "Abu Dhabi": "https://www.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Abu_Dhabi_Circuit.png.transform/9col/image.png"
        }
        
        # 根据国家或地点匹配赛道图片
        image_url = None
        for key, url in circuit_images.items():
            if key.lower() in race_info['Country'].lower() or key.lower() in race_info['Location'].lower() or key.lower() in race_info['EventName'].lower():
                image_url = url
                break
        
        # 特殊情况处理
        if not image_url:
            location_lower = race_info['Location'].lower()
            event_name_lower = race_info['EventName'].lower()
            
            if 'yas' in location_lower or 'abu dhabi' in event_name_lower:
                image_url = circuit_images['Abu Dhabi']
            elif 'silverstone' in location_lower or 'britain' in event_name_lower:
                image_url = circuit_images['Great Britain']
            elif 'monza' in location_lower or 'italy' in event_name_lower:
                image_url = circuit_images['Italy']
            elif 'spa' in location_lower or 'belgium' in event_name_lower:
                image_url = circuit_images['Belgium']
            elif 'monaco' in location_lower or 'monte carlo' in location_lower:
                image_url = circuit_images['Monaco']
        
        circuit_data["image_url"] = image_url
        
        # 缓存1年（赛道信息很少变化）
        set_cache(cache_key, circuit_data, int(timedelta(days=365).total_seconds()))
        return circuit_data
        
    except Exception as e:
        raise Exception(f"Circuit info error: {str(e)}") 