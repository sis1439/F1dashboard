from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd
import fastf1
from cache_utils import get_cache, set_cache

def get_race_results(year: int, round: int) -> Dict[str, Any]:
    """获取完整的比赛周末数据"""
    cache_key = f"race_results_{year}_{round}"
    cached_data = get_cache(cache_key)
    
    if cached_data:
        return cached_data
    
    try:
        # 获取比赛事件
        schedule = fastf1.get_event_schedule(year)
        race_info = schedule[schedule['RoundNumber'] == round].iloc[0]
        
        session = fastf1.get_session(year, round, 'R')  # 比赛会话
        session.load()
        
        # 比赛结果
        results = []
        for _, driver in session.results.iterrows():
            results.append({
                "position": int(driver['Position']) if pd.notna(driver['Position']) else None,
                "driver": driver['FullName'],
                "team": driver['TeamName'],
                "time": str(driver['Time']) if pd.notna(driver['Time']) else None,
                "points": float(driver['Points']) if pd.notna(driver['Points']) else 0,
                "status": driver['Status']
            })
        
        race_data = {
            "race_info": {
                "round": int(race_info['RoundNumber']),
                "race_name": race_info['EventName'],
                "location": race_info['Location'],
                "country": race_info['Country'],
                "date": race_info['EventDate'].strftime('%Y-%m-%d')
            },
            "results": results
        }
        
        # 缓存完成的比赛1个月（它们不会改变）
        set_cache(cache_key, race_data, int(timedelta(days=30).total_seconds()))
        return race_data
        
    except Exception as e:
        raise Exception(f"Race results error: {str(e)}")

def get_qualifying_results(year: int, round: int) -> List[Dict[str, Any]]:
    """获取特定比赛的排位赛结果"""
    cache_key = f"race_qualifying_{year}_{round}"
    cached_data = get_cache(cache_key)
    
    if cached_data:
        return cached_data
    
    try:
        session = fastf1.get_session(year, round, 'Q')  # 排位赛会话
        session.load()
        
        qualifying_results = []
        for _, driver in session.results.iterrows():
            qualifying_results.append({
                "position": int(driver['Position']) if pd.notna(driver['Position']) else None,
                "driver": driver['FullName'],
                "team": driver['TeamName'],
                "q1": str(driver['Q1']) if pd.notna(driver['Q1']) else None,
                "q2": str(driver['Q2']) if pd.notna(driver['Q2']) else None,
                "q3": str(driver['Q3']) if pd.notna(driver['Q3']) else None
            })
        
        # 缓存1个月
        set_cache(cache_key, qualifying_results, int(timedelta(days=30).total_seconds()))
        return qualifying_results
        
    except Exception as e:
        raise Exception(f"Qualifying results error: {str(e)}")

def get_practice_results(year: int, round: int, session: str = "FP1") -> List[Dict[str, Any]]:
    """获取练习赛会话结果 (FP1, FP2, FP3)"""
    cache_key = f"race_practice_{year}_{round}_{session}"
    cached_data = get_cache(cache_key)
    
    if cached_data:
        return cached_data
    
    try:
        practice_session = fastf1.get_session(year, round, session)
        practice_session.load()
        
        practice_results = []
        for _, driver in practice_session.results.iterrows():
            practice_results.append({
                "position": int(driver['Position']) if pd.notna(driver['Position']) else None,
                "driver": driver['FullName'],
                "team": driver['TeamName'],
                "time": str(driver['Time']) if pd.notna(driver['Time']) else None,
                "gap": str(driver['Gap']) if pd.notna(driver['Gap']) else None,
                "laps": int(driver['Laps']) if pd.notna(driver['Laps']) else 0
            })
        
        # 缓存1个月
        set_cache(cache_key, practice_results, int(timedelta(days=30).total_seconds()))
        return practice_results
        
    except Exception as e:
        raise Exception(f"Practice results error: {str(e)}")

def get_race_summary(year: int, round: int) -> Dict[str, Any]:
    """获取比赛周末所有会话的摘要"""
    cache_key = f"race_summary_{year}_{round}"
    cached_data = get_cache(cache_key)
    
    if cached_data:
        return cached_data
    
    try:
        # 获取基本比赛信息
        schedule = fastf1.get_event_schedule(year)
        race_info = schedule[schedule['RoundNumber'] == round].iloc[0]
        
        summary = {
            "race_info": {
                "round": int(race_info['RoundNumber']),
                "race_name": race_info['EventName'],
                "location": race_info['Location'],
                "country": race_info['Country'],
                "date": race_info['EventDate'].strftime('%Y-%m-%d')
            },
            "sessions_available": []
        }
        
        # 检查哪些会话可用
        sessions = ['FP1', 'FP2', 'FP3', 'Q', 'R']
        for session_type in sessions:
            try:
                session = fastf1.get_session(year, round, session_type)
                if session is not None:
                    summary["sessions_available"].append({
                        "session": session_type,
                        "name": {
                            'FP1': 'Free Practice 1',
                            'FP2': 'Free Practice 2', 
                            'FP3': 'Free Practice 3',
                            'Q': 'Qualifying',
                            'R': 'Race'
                        }.get(session_type, session_type)
                    })
            except:
                continue
        
        # 缓存1周
        set_cache(cache_key, summary, int(timedelta(weeks=1).total_seconds()))
        return summary
        
    except Exception as e:
        raise Exception(f"Race summary error: {str(e)}") 