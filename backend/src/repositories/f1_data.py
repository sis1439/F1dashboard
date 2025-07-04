import fastf1
import requests
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
from config.settings import settings

logger = logging.getLogger(__name__)


class F1DataRepository:
    """Repository for accessing F1 data from various sources"""
    
    def __init__(self):
        """Initialize F1 data repository"""
        # Note: FastF1 cache is initialized in main.py startup
        self.ergast_base_url = "https://api.jolpi.ca/ergast/f1"
    
    # FastF1 Data Access Methods
    
    def get_event_schedule(self, year: int) -> pd.DataFrame:
        """Get F1 event schedule for a year using FastF1"""
        try:
            return fastf1.get_event_schedule(year)
        except Exception as e:
            logger.error(f"Error getting event schedule for {year}: {e}")
            raise
    
    def get_session(self, year: int, round_num: int, session: str):
        """Get F1 session data using FastF1"""
        try:
            return fastf1.get_session(year, round_num, session)
        except Exception as e:
            logger.error(f"Error getting session {session} for {year} round {round_num}: {e}")
            raise
    
    def load_session_data(self, session, laps: bool = True, telemetry: bool = False, 
                         weather: bool = False, messages: bool = False):
        """Load session data with specified options"""
        try:
            session.load(laps=laps, telemetry=telemetry, weather=weather, messages=messages)
            return session
        except Exception as e:
            logger.error(f"Error loading session data: {e}")
            raise
    
    # Ergast API Methods
    
    def get_driver_standings_ergast(self, year: int, round_num: Optional[int] = None) -> Dict[str, Any]:
        """Get driver standings from Ergast API"""
        try:
            if round_num:
                url = f"{self.ergast_base_url}/{year}/{round_num}/driverStandings.json"
            else:
                url = f"{self.ergast_base_url}/{year}/driverStandings.json"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting driver standings from Ergast: {e}")
            raise
    
    def get_constructor_standings_ergast(self, year: int, round_num: Optional[int] = None) -> Dict[str, Any]:
        """Get constructor standings from Ergast API"""
        try:
            if round_num:
                url = f"{self.ergast_base_url}/{year}/{round_num}/constructorStandings.json"
            else:
                url = f"{self.ergast_base_url}/{year}/constructorStandings.json"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting constructor standings from Ergast: {e}")
            raise
    
    def get_latest_round_ergast(self, year: int) -> int:
        """Get the latest round number for a year from Ergast API"""
        try:
            url = f"{self.ergast_base_url}/{year}/driverStandings.json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            standings_list = data.get('MRData', {}).get('StandingsTable', {}).get('StandingsLists', [])
            if standings_list:
                return int(standings_list[0].get('round', 1))
            return 1
        except Exception as e:
            logger.error(f"Error getting latest round from Ergast: {e}")
            return 1
    
    # Time Formatting Utilities
    
    def format_lap_time(self, time_obj) -> Optional[str]:
        """Format lap time to mm:ss.sss format"""
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
        except Exception as e:
            logger.error(f"Error formatting lap time: {e}")
            return None
    
    def format_race_time(self, time_obj) -> Optional[str]:
        """Format race time to h:mm:ss.sss format, removing day component"""
        if pd.isna(time_obj) or time_obj is None:
            return None
        
        try:
            if hasattr(time_obj, 'total_seconds'):
                total_seconds = time_obj.total_seconds()
            elif hasattr(time_obj, 'days') and hasattr(time_obj, 'seconds'):
                # Handle timedelta objects with days, only take time components
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
        except Exception as e:
            logger.error(f"Error formatting race time: {e}")
            return None
    
    # Validation Methods
    
    def validate_year(self, year: int) -> bool:
        """Validate if year is within acceptable range"""
        current_year = datetime.now().year
        return 1950 <= year <= current_year + 1
    
    def validate_round(self, year: int, round_num: int) -> bool:
        """Validate if round number is valid for the given year"""
        try:
            schedule = self.get_event_schedule(year)
            max_round = schedule['RoundNumber'].max()
            return 1 <= round_num <= max_round
        except Exception:
            # If we can't validate, assume it's valid and let the API handle it
            return True


# Global F1 data repository instance
f1_data_repo = F1DataRepository() 