from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import fastf1
import redis
import json
import pandas as pd
from datetime import datetime, timedelta

app = FastAPI()

# Allow frontend cross-origin access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def get_next_race_date(year: int = None):
    """Get the next race date for smart cache expiration"""
    if year is None:
        year = datetime.now().year
    
    try:
        schedule = fastf1.get_event_schedule(year)
        now = datetime.now()
        
        # Find next race (EventDate is in the future)
        future_races = schedule[pd.to_datetime(schedule['EventDate']) > now]
        
        if not future_races.empty:
            next_race_date = pd.to_datetime(future_races.iloc[0]['EventDate'])
            return next_race_date
        else:
            # If no future races this year, cache for 1 week
            return now + timedelta(weeks=1)
    except:
        # Fallback: cache for 1 week
        return datetime.now() + timedelta(weeks=1)

def get_cache_expiry_seconds(year: int = None):
    """Calculate cache expiry time until next race"""
    next_race = get_next_race_date(year)
    now = datetime.now()
    
    # Cache until next race, but minimum 1 hour, maximum 1 week
    seconds_until_race = int((next_race - now).total_seconds())
    return max(3600, min(seconds_until_race, 604800))  # 1 hour to 1 week

@app.get("/api/available-years")
def get_available_years():
    # Check Redis cache first
    cache_key = "available_years"
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        return json.loads(cached_data)
    
    # From 1950 (F1 starting year) to current year
    current_year = datetime.now().year
    years = list(range(2023, current_year + 1))
    
    # Cache for 1 week (years don't change often)
    redis_client.setex(cache_key, timedelta(weeks=1), json.dumps(years))
    
    return years

@app.get("/api/driver-standings")
def driver_standings(year: int = None):
    # Get current year
    if year is None:
        year = datetime.now().year

    # Check Redis cache first
    cache_key = f"driver_standings_{year}"
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        return json.loads(cached_data)

    try:
        # Use Jolpica-F1 API (Ergast successor)
        import requests
        
        # Get the latest standings for the year
        url = f"https://api.jolpi.ca/ergast/f1/{year}/driverStandings.json"
        response = requests.get(url)
        
        if response.status_code != 200:
            return {"error": f"Failed to fetch driver standings for {year}"}
        
        data_json = response.json()
        standings_list = data_json.get('MRData', {}).get('StandingsTable', {}).get('StandingsLists', [])
        
        if not standings_list:
            return {"error": f"No driver standings data available for {year}"}
        
        driver_standings = standings_list[0].get('DriverStandings', [])
        
        # Only take top ten
        driver_standings = driver_standings[:10]
        
        data = []
        for standing in driver_standings:
            driver = standing.get('Driver', {})
            data.append({
                "pos": int(standing.get('position', 0)),
                "name": f"{driver.get('givenName', '')} {driver.get('familyName', '')}",
                "points": float(standing.get('points', 0)),
                "evo": 0  # Can be customized
            })
        
        # Cache until next race
        cache_seconds = get_cache_expiry_seconds(year)
        redis_client.setex(cache_key, cache_seconds, json.dumps(data))
        
        return data
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/constructor-standings")
def constructor_standings(year: int = None):
    # Get current year
    if year is None:
        year = datetime.now().year
    
    # Check Redis cache first
    cache_key = f"constructor_standings_{year}"
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        return json.loads(cached_data)
    
    try:
        # Use Jolpica-F1 API (Ergast successor)
        import requests
        
        # Get the latest standings for the year
        url = f"https://api.jolpi.ca/ergast/f1/{year}/constructorStandings.json"
        response = requests.get(url)
        
        if response.status_code != 200:
            return {"error": f"Failed to fetch constructor standings for {year}"}
        
        data_json = response.json()
        standings_list = data_json.get('MRData', {}).get('StandingsTable', {}).get('StandingsLists', [])
        
        if not standings_list:
            return {"error": f"No constructor standings data available for {year}"}
        
        constructor_standings = standings_list[0].get('ConstructorStandings', [])
        
        # Only take top ten
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
        
        # Cache until next race
        cache_seconds = get_cache_expiry_seconds(year)
        redis_client.setex(cache_key, cache_seconds, json.dumps(data))
        
        return data
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/next-race")
def get_next_race_info(year: int = None):
    """Get next race information"""
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
        return {"error": str(e)}

@app.get("/api/clear-cache")
def clear_cache():
    """Clear all F1 related cache - useful for development"""
    keys = redis_client.keys("driver_standings_*") + redis_client.keys("constructor_standings_*") + redis_client.keys("available_years")
    if keys:
        redis_client.delete(*keys)
        return {"message": f"Cleared {len(keys)} cache entries"}
    return {"message": "No cache entries to clear"}

@app.get("/api/race-schedule")
def get_race_schedule(year: int = None):
    """Get full race schedule for a year"""
    if year is None:
        year = datetime.now().year
    
    cache_key = f"race_schedule_{year}"
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        return json.loads(cached_data)
    
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
        
        # Cache for 1 week (schedule rarely changes)
        redis_client.setex(cache_key, timedelta(weeks=1), json.dumps(races))
        return races
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/race-results")
def get_race_results(year: int, round: int):
    """Get complete race weekend data for a specific race"""
    cache_key = f"race_results_{year}_{round}"
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        return json.loads(cached_data)
    
    try:
        # Get race event
        schedule = fastf1.get_event_schedule(year)
        race_info = schedule[schedule['RoundNumber'] == round].iloc[0]
        
        session = fastf1.get_session(year, round, 'R')  # Race session
        session.load()
        
        # Race results
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
        
        # Cache completed races for 1 month (they don't change)
        redis_client.setex(cache_key, timedelta(days=30), json.dumps(race_data))
        return race_data
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/qualifying-results")
def get_qualifying_results(year: int, round: int):
    """Get qualifying results for a specific race"""
    cache_key = f"race_qualifying_{year}_{round}"
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        return json.loads(cached_data)
    
    try:
        session = fastf1.get_session(year, round, 'Q')  # Qualifying session
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
        
        # Cache for 1 month
        redis_client.setex(cache_key, timedelta(days=30), json.dumps(qualifying_results))
        return qualifying_results
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/practice-results")
def get_practice_results(year: int, round: int, session: str = "FP1"):
    """Get practice session results (FP1, FP2, FP3)"""
    cache_key = f"race_practice_{year}_{round}_{session}"
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        return json.loads(cached_data)
    
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
        
        # Cache for 1 month
        redis_client.setex(cache_key, timedelta(days=30), json.dumps(practice_results))
        return practice_results
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/race-summary")
def get_race_summary(year: int, round: int):
    """Get a summary of all sessions for a race weekend"""
    cache_key = f"race_summary_{year}_{round}"
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        return json.loads(cached_data)
    
    try:
        # Get basic race info
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
        
        # Check which sessions are available
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
        
        # Cache for 1 week
        redis_client.setex(cache_key, timedelta(weeks=1), json.dumps(summary))
        return summary
        
    except Exception as e:
        return {"error": str(e)}

