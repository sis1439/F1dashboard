from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd
import fastf1
from cache_utils import get_cache, set_cache

def format_lap_time(time_obj):
    """将时间对象格式化为 mm:ss.sss 格式"""
    if pd.isna(time_obj) or time_obj is None:
        return None
    
    try:
        if hasattr(time_obj, 'total_seconds'):
            total_seconds = time_obj.total_seconds()
        else:
            total_seconds = float(time_obj)
        
        if total_seconds <= 0:
            return None
            
        minutes = int(total_seconds // 60)
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:06.3f}"
    except:
        return None

def format_race_time(time_obj):
    """将比赛时间对象格式化为 h:mm:ss.sss 格式，去掉天数部分"""
    if pd.isna(time_obj) or time_obj is None:
        return None
    
    try:
        if hasattr(time_obj, 'total_seconds'):
            total_seconds = time_obj.total_seconds()
        elif hasattr(time_obj, 'days') and hasattr(time_obj, 'seconds'):
            # 处理包含天数的timedelta对象，只取时分秒部分
            total_seconds = time_obj.seconds + time_obj.microseconds / 1000000
        else:
            total_seconds = float(time_obj)
        
        if total_seconds <= 0:
            return None
            
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:06.3f}"
        else:
            return f"{minutes:02d}:{seconds:06.3f}"
    except:
        return None

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
        session.load(laps=True, telemetry=False, weather=False, messages=False)
        
        # 从 session.laps 计算每个车手的总圈数
        lap_counts = {}
        if session.laps is not None and not session.laps.empty:
            lap_counts = session.laps.groupby('Driver')['LapNumber'].max().to_dict()

        results = []
        
        # 直接使用官方结果数据
        print(f"Using official results data for {year} round {round}")
        if not session.results.empty:
            for _, driver in session.results.iterrows():
                position = int(driver['Position']) if pd.notna(driver['Position']) else None
                driver_time = driver.get('Time')
                
                # 处理时间显示：第一名显示完整时间，其他车手显示完整时间+gap
                formatted_time = None
                gap = None
                
                if position == 1 and pd.notna(driver_time):
                    # 第一名显示完整的比赛时间
                    formatted_time = format_race_time(driver_time)
                    gap = None
                elif position and position > 1 and pd.notna(driver_time):
                    # 其他车手：需要计算完整时间和gap
                    # driver_time是与第一名的时间差
                    gap_seconds = driver_time.total_seconds()
                    gap = f"+{gap_seconds:.3f}s"
                    
                    # 获取第一名的完整时间来计算其他车手的完整时间
                    first_driver = session.results.iloc[0]
                    first_time = first_driver.get('Time')
                    if pd.notna(first_time):
                        # 其他车手的完整时间 = 第一名时间 + 时间差
                        full_time = first_time + driver_time
                        formatted_time = format_race_time(full_time)
                
                # 处理Laps数据，确保正确显示
                driver_abbr = driver.get('Abbreviation')
                laps_value = lap_counts.get(driver_abbr)
                if pd.notna(laps_value):
                    laps_value = int(laps_value)
                else:
                    laps_value = 0
                
                # 处理状态数据
                status = driver.get('Status', 'Unknown')
                if pd.isna(status) or status == '':
                    # 如果没有状态信息，根据position和laps推测
                    if position and position <= 20:
                        status = "Finished"
                    else:
                        status = "DNF"
                
                results.append({
                    "position": position,
                    "driver": driver['FullName'],
                    "team": driver['TeamName'],
                    "time": formatted_time,
                    "gap": gap,  # 第一名为None，其他为+X.XXXs格式
                    "points": float(driver['Points']) if pd.notna(driver['Points']) else 0,
                    "status": status,
                    "laps": laps_value
                })
        else:
            print(f"No official results data available for {year} round {round}")
        
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
        print(f"Race results error for {year} round {round}: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"results": []}

def get_qualifying_results(year: int, round: int) -> List[Dict[str, Any]]:
    """获取特定比赛的排位赛结果"""
    cache_key = f"race_qualifying_{year}_{round}"
    cached_data = get_cache(cache_key)
    
    if cached_data:
        return cached_data
    
    try:
        session = fastf1.get_session(year, round, 'Q')  # 排位赛会话
        session.load(laps=True, telemetry=False, weather=False, messages=False)
        
        # 从 session.laps 计算每个车手的总圈数
        lap_counts = {}
        if session.laps is not None and not session.laps.empty:
            lap_counts = session.laps.groupby('Driver')['LapNumber'].max().to_dict()

        qualifying_results = []
        for _, driver in session.results.iterrows():
            driver_abbr = driver.get('Abbreviation')
            laps_value = lap_counts.get(driver_abbr)
            if pd.notna(laps_value):
                laps_value = int(laps_value)
            else:
                laps_value = 0

            qualifying_results.append({
                "position": int(driver['Position']) if pd.notna(driver['Position']) else None,
                "driver": driver['FullName'],
                "team": driver['TeamName'],
                "q1": format_lap_time(driver['Q1']),
                "q2": format_lap_time(driver['Q2']),
                "q3": format_lap_time(driver['Q3']),
                "laps": laps_value
            })
        
        # 缓存1个月
        set_cache(cache_key, qualifying_results, int(timedelta(days=30).total_seconds()))
        return qualifying_results
        
    except Exception as e:
        print(f"Qualifying results error for {year} round {round}: {str(e)}")
        return []

def get_practice_results(year: int, round: int, session: str = "FP1") -> List[Dict[str, Any]]:
    """获取练习赛会话结果 (FP1, FP2, FP3, SQ, S)"""
    cache_key = f"race_practice_{year}_{round}_{session}"
    cached_data = get_cache(cache_key)
    
    if cached_data:
        return cached_data
    
    try:
        # 获取会话
        session_obj = fastf1.get_session(year, round, session)
        if session_obj is None:
            return []
            
        session_obj.load(laps=True)
        results = []
        
        # 判断会话类型
        is_sprint_session = session in ['S', 'Sprint']
        is_sprint_qualifying = session in ['SQ', 'Sprint Qualifying']
        
        if is_sprint_session:
            # Sprint会话：类似于比赛，有Position、Time等字段
            if hasattr(session_obj, 'results') and session_obj.results is not None and not session_obj.results.empty:
                # 从 session.laps 计算每个车手的总圈数
                lap_counts = {}
                if session_obj.laps is not None and not session_obj.laps.empty:
                    lap_counts = session_obj.laps.groupby('Driver')['LapNumber'].max().to_dict()

                for _, driver in session_obj.results.iterrows():
                    position = int(driver['Position']) if pd.notna(driver['Position']) else None
                    driver_time = driver.get('Time')
                    
                    # 处理时间显示：第一名显示完整时间，其他车手显示完整时间+gap
                    formatted_time = None
                    gap = None
                    
                    if position == 1 and pd.notna(driver_time):
                        # 第一名显示完整的Sprint时间
                        formatted_time = format_race_time(driver_time)
                        gap = None
                    elif position and position > 1 and pd.notna(driver_time):
                        # 其他车手：需要计算完整时间和gap
                        gap_seconds = driver_time.total_seconds()
                        gap = f"+{gap_seconds:.3f}s"
                        
                        # 获取第一名的完整时间来计算其他车手的完整时间
                        first_driver = session_obj.results.iloc[0]
                        first_time = first_driver.get('Time')
                        if pd.notna(first_time):
                            # 其他车手的完整时间 = 第一名时间 + 时间差
                            full_time = first_time + driver_time
                            formatted_time = format_race_time(full_time)
                    
                    # 处理Laps数据
                    driver_abbr = driver.get('Abbreviation')
                    laps_value = lap_counts.get(driver_abbr)
                    if pd.notna(laps_value):
                        laps_value = int(laps_value)
                    else:
                        laps_value = 0
                    
                    # 处理状态数据
                    status = driver.get('Status', 'Unknown')
                    if pd.isna(status) or status == '':
                        if position and position <= 20:
                            status = "Finished"
                        else:
                            status = "DNF"
                    
                    results.append({
                        "position": position,
                        "driver": driver['FullName'],
                        "team": driver['TeamName'],
                        "time": formatted_time,
                        "gap": gap,
                        "points": float(driver['Points']) if pd.notna(driver['Points']) else 0,
                        "status": status,
                        "laps": laps_value
                    })
        else:
            # 练习赛和Sprint Qualifying会话：显示最快圈速和差距
            # 从 session.laps 计算每个车手的总圈数和最快圈速
            lap_counts = {}
            best_times = {}
            fastest_overall = None
            
            if session_obj.laps is not None and not session_obj.laps.empty:
                lap_counts = session_obj.laps.groupby('Driver')['LapNumber'].max().to_dict()
                
                # 计算每个车手的最快圈速
                valid_laps = session_obj.laps[session_obj.laps['LapTime'].notna()]
                if not valid_laps.empty:
                    best_times = valid_laps.groupby('Driver')['LapTime'].min().to_dict()
                    # 找到全场最快圈速
                    fastest_overall = valid_laps['LapTime'].min()

            if hasattr(session_obj, 'results') and session_obj.results is not None and not session_obj.results.empty:
                for idx, (_, driver) in enumerate(session_obj.results.iterrows(), 1):
                    # 练习赛和Sprint Qualifying会话没有Position字段，使用索引作为排名
                    position = idx
                    
                    driver_abbr = driver.get('Abbreviation')
                    laps_value = lap_counts.get(driver_abbr)
                    if pd.notna(laps_value):
                        laps_value = int(laps_value)
                    else:
                        laps_value = 0

                    # 获取车手的最快圈速
                    best_time = best_times.get(driver_abbr)
                    best_time_str = format_lap_time(best_time) if best_time and pd.notna(best_time) else None
                    
                    # 计算与全场最快圈速的差距
                    gap_to_fastest = None
                    if best_time and pd.notna(best_time) and fastest_overall and pd.notna(fastest_overall):
                        if best_time != fastest_overall:
                            gap_seconds = (best_time - fastest_overall).total_seconds()
                            if gap_seconds > 0:
                                gap_to_fastest = f"+{gap_seconds:.3f}s"

                    results.append({
                        "position": position,
                        "driver": str(driver.get('FullName', driver.get('Driver', 'Unknown'))),
                        "team": str(driver.get('TeamName', driver.get('Team', 'Unknown'))),
                        "time": best_time_str,      # Best Time 显示在 time 字段
                        "gap": gap_to_fastest,      # Gap to Fastest 显示在 gap 字段
                        "laps": laps_value
                    })
        
        # 缓存结果
        set_cache(cache_key, results, int(timedelta(days=30).total_seconds()))
        return results
        
    except Exception as e:
        print(f"Practice results error for {year} round {round} session {session}: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

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
        
        # 检查所有可能的会话类型，包括Sprint周末的会话
        all_possible_sessions = ['FP1', 'FP2', 'FP3', 'SQ', 'S', 'Q', 'R']
        session_names = {
            'FP1': 'Practice 1',
            'FP2': 'Practice 2', 
            'FP3': 'Practice 3',
            'SQ': 'Sprint Qualifying',
            'S': 'Sprint',
            'Q': 'Qualifying',
            'R': 'Race'
        }
        
        for session_type in all_possible_sessions:
            try:
                session = fastf1.get_session(year, round, session_type)
                if session is not None:
                    # 尝试检查会话是否有数据
                    try:
                        session.load(laps=False, telemetry=False, weather=False, messages=False)
                        has_results = hasattr(session, 'results') and session.results is not None
                        if has_results and not session.results.empty:
                            summary["sessions_available"].append({
                                "session": session_type,
                                "name": session_names.get(session_type, session_type),
                                "key": session_names.get(session_type, session_type).replace(' ', '_').lower()
                            })
                    except Exception:
                        # load 失败通常说明该会话并未真的举行或数据暂不可用，直接跳过
                        continue
            except:
                continue
        
        # 缓存1周
        set_cache(cache_key, summary, int(timedelta(weeks=1).total_seconds()))
        return summary
        
    except Exception as e:
        raise Exception(f"Race summary error: {str(e)}") 