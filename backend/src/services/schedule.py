from typing import List, Optional
from datetime import datetime, timedelta
import pandas as pd
import logging
from repositories.cache import cache_repo
from repositories.f1_data import f1_data_repo
from models.schedule import (
    RaceScheduleItem, RaceScheduleResponse, AvailableYearsResponse,
    NextRaceInfo, NextRaceResponse, SessionInfo, CircuitInfo,
    RaceInfo, RaceWeekendScheduleResponse
)
from utils.constants import SESSION_TYPES, SESSION_DURATIONS
from utils.time_utils import calculate_session_status
from config.settings import settings

logger = logging.getLogger(__name__)


class ScheduleService:
    """Service for handling F1 schedule business logic"""
    
    def __init__(self):
        self.cache_repo = cache_repo
        self.f1_data_repo = f1_data_repo
    
    def get_available_years(self) -> AvailableYearsResponse:
        """Get available years for F1 data"""
        cache_key = "available_years"
        cached_data = self.cache_repo.get(cache_key)
        
        if cached_data:
            logger.info("Available years cache hit")
            return AvailableYearsResponse(
                data=cached_data,
                cache_info=self.cache_repo.get_cache_info(cache_key)
            )
        
        try:
            # From 2023 to current year
            current_year = datetime.now().year
            years = list(range(2023, current_year + 1))
            
            # Cache for 1 week (years don't change often)
            self.cache_repo.set(cache_key, years, int(timedelta(weeks=1).total_seconds()))
            
            return AvailableYearsResponse(
                data=years,
                cache_info=self.cache_repo.get_cache_info(cache_key)
            )
            
        except Exception as e:
            logger.error(f"Error getting available years: {e}")
            raise
    
    def get_race_schedule(self, year: Optional[int] = None) -> RaceScheduleResponse:
        """Get complete season race schedule"""
        if year is None:
            year = datetime.now().year
        
        # Validate year
        if not self.f1_data_repo.validate_year(year):
            raise ValueError(f"Invalid year: {year}")
        
        cache_key = f"race_schedule_{year}"
        cached_data = self.cache_repo.get(cache_key)
        
        if cached_data:
            logger.info(f"Race schedule cache hit for {year}")
            return RaceScheduleResponse(
                data=cached_data,
                year=year,
                cache_info=self.cache_repo.get_cache_info(cache_key)
            )
        
        try:
            logger.info(f"Fetching race schedule for {year}")
            schedule_df = self.f1_data_repo.get_event_schedule(year)
            
            races = []
            for _, race in schedule_df.iterrows():
                races.append(RaceScheduleItem(
                    round=int(race['RoundNumber']),
                    race_name=race['EventName'],
                    location=race['Location'],
                    country=race['Country'],
                    date=race['EventDate'].strftime('%Y-%m-%d'),
                    format=race.get('EventFormat', 'Conventional')
                ))
            
            # Transform to dict for caching
            races_data = [race.dict() for race in races]
            
            # Cache for 1 week (schedule rarely changes)
            self.cache_repo.set(cache_key, races_data, settings.cache_ttl_schedule)
            
            return RaceScheduleResponse(
                data=races,
                year=year,
                cache_info=self.cache_repo.get_cache_info(cache_key)
            )
            
        except Exception as e:
            logger.error(f"Error getting race schedule for {year}: {e}")
            raise
    
    def get_next_race_info(self, year: Optional[int] = None) -> NextRaceResponse:
        """Get next race information"""
        if year is None:
            year = datetime.now().year
        
        try:
            logger.info(f"Getting next race info for {year}")
            schedule_df = self.f1_data_repo.get_event_schedule(year)
            now = datetime.now()
            
            future_races = schedule_df[pd.to_datetime(schedule_df['EventDate']) > now]
            
            if not future_races.empty:
                next_race = future_races.iloc[0]
                next_race_info = NextRaceInfo(
                    race_name=next_race['EventName'],
                    date=next_race['EventDate'].strftime('%Y-%m-%d'),
                    location=next_race['Location'],
                    country=next_race['Country']
                )
                
                return NextRaceResponse(data=next_race_info)
            else:
                # No upcoming races this year
                return NextRaceResponse(
                    success=False,
                    message="No upcoming races this year"
                )
                
        except Exception as e:
            logger.error(f"Error getting next race info: {e}")
            raise
    
    def get_race_weekend_schedule(self, year: Optional[int] = None, round_num: Optional[int] = None) -> RaceWeekendScheduleResponse:
        """Get detailed race weekend schedule with all sessions"""
        if year is None:
            year = datetime.now().year
        
        # If no round specified, get next race
        if round_num is None:
            try:
                schedule_df = self.f1_data_repo.get_event_schedule(year)
                now = datetime.now()
                now_timestamp = pd.Timestamp(now.date())
                future_races = schedule_df[pd.to_datetime(schedule_df['EventDate']) >= now_timestamp]
                if not future_races.empty:
                    next_race = future_races.iloc[0]
                    round_num = int(next_race['RoundNumber'])
                else:
                    # If no future races this year, get the last race
                    last_race = schedule_df.iloc[-1]
                    round_num = int(last_race['RoundNumber'])
            except Exception as e:
                raise ValueError(f"Could not determine race round: {str(e)}")
        
        # Validate inputs
        if not self.f1_data_repo.validate_year(year):
            raise ValueError(f"Invalid year: {year}")
        
        cache_key = f"race_weekend_schedule_{year}_{round_num}"
        cached_data = self.cache_repo.get(cache_key)
        
        if cached_data:
            logger.info(f"Race weekend schedule cache hit for {year} round {round_num}")
            return RaceWeekendScheduleResponse(
                race_info=cached_data["race_info"],
                sessions=cached_data["sessions"],
                circuit=cached_data["circuit"],
                cache_info=self.cache_repo.get_cache_info(cache_key)
            )
        
        try:
            logger.info(f"Fetching race weekend schedule for {year} round {round_num}")
            schedule_df = self.f1_data_repo.get_event_schedule(year)
            race_info_df = schedule_df[schedule_df['RoundNumber'] == round_num].iloc[0]
            
            # Build race info
            race_info = RaceInfo(
                round=int(race_info_df['RoundNumber']),
                race_name=race_info_df['EventName'],
                location=race_info_df['Location'],
                country=race_info_df['Country'],
                date=race_info_df['EventDate'].strftime('%Y-%m-%d'),
                official_name=race_info_df.get('OfficialEventName', race_info_df['EventName'])
            )
            
            # Build sessions list
            sessions = []
            session_mapping = {
                'Session1Date': {'name': 'Practice 1', 'code': 'FP1'},
                'Session2Date': {'name': 'Practice 2', 'code': 'FP2'},
                'Session3Date': {'name': 'Practice 3', 'code': 'FP3'},
                'Session4Date': {'name': 'Qualifying', 'code': 'Q'},
                'Session5Date': {'name': 'Race', 'code': 'R'}
            }
            
            current_time = datetime.now()
            
            for session_date_col, session_info in session_mapping.items():
                if session_date_col in race_info_df and pd.notna(race_info_df[session_date_col]):
                    session_datetime = race_info_df[session_date_col]
                    if isinstance(session_datetime, str):
                        session_datetime = pd.to_datetime(session_datetime)
                    
                    # Calculate end time
                    duration_minutes = SESSION_DURATIONS.get(session_info['code'], 90)
                    end_datetime = session_datetime + pd.Timedelta(minutes=duration_minutes)
                    
                    # Determine status
                    status = calculate_session_status(session_datetime, end_datetime, current_time)
                    
                    sessions.append(SessionInfo(
                        name=session_info['name'],
                        code=session_info['code'],
                        date=session_datetime.strftime('%Y-%m-%d'),
                        time=session_datetime.strftime('%H:%M'),
                        datetime=session_datetime.isoformat(),
                        end_datetime=end_datetime.isoformat(),
                        end_time=end_datetime.strftime('%H:%M'),
                        status=status,
                        duration_minutes=duration_minutes
                    ))
            
            # Build circuit info
            circuit = CircuitInfo(
                name=race_info_df.get('CircuitShortName', ''),
                location=race_info_df['Location'],
                country=race_info_df['Country']
            )
            
            # Prepare data for caching
            response_data = {
                "race_info": race_info.dict(),
                "sessions": [session.dict() for session in sessions],
                "circuit": circuit.dict()
            }
            
            # Cache for 1 hour (race times might have minor adjustments)
            self.cache_repo.set(cache_key, response_data, 3600)
            
            return RaceWeekendScheduleResponse(
                race_info=race_info,
                sessions=sessions,
                circuit=circuit,
                cache_info=self.cache_repo.get_cache_info(cache_key)
            )
            
        except Exception as e:
            logger.error(f"Error getting race weekend schedule: {e}")
            raise
    
    def get_circuit_info(self, year: Optional[int] = None, round_num: Optional[int] = None) -> dict:
        """Get circuit information including circuit image URLs"""
        if year is None:
            year = datetime.now().year
        
        # If no round specified, get next race
        if round_num is None:
            try:
                schedule_df = self.f1_data_repo.get_event_schedule(year)
                now = datetime.now()
                now_timestamp = pd.Timestamp(now.date())
                future_races = schedule_df[pd.to_datetime(schedule_df['EventDate']) >= now_timestamp]
                if not future_races.empty:
                    next_race = future_races.iloc[0]
                    round_num = int(next_race['RoundNumber'])
                else:
                    # If no future races this year, get the last race
                    last_race = schedule_df.iloc[-1]
                    round_num = int(last_race['RoundNumber'])
            except Exception as e:
                raise ValueError(f"Could not determine race round: {str(e)}")
        
        cache_key = f"circuit_info_{year}_{round_num}"
        cached_data = self.cache_repo.get(cache_key)
        
        if cached_data:
            logger.info(f"Circuit info cache hit for {year} round {round_num}")
            return cached_data
        
        try:
            logger.info(f"Fetching circuit info for {year} round {round_num}")
            schedule_df = self.f1_data_repo.get_event_schedule(year)
            race_info = schedule_df[schedule_df['RoundNumber'] == round_num].iloc[0]
            
            # Basic circuit information
            circuit_data = {
                "name": race_info.get('CircuitShortName', ''),
                "location": race_info['Location'],
                "country": race_info['Country'],
                "round": round_num,
                "race_name": race_info['EventName']
            }
            
            # Circuit image URL mapping (based on circuit name)
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
            
            # Match circuit image based on country or location
            image_url = None
            for key, url in circuit_images.items():
                if (key.lower() in race_info['Country'].lower() or 
                    key.lower() in race_info['Location'].lower() or 
                    key.lower() in race_info['EventName'].lower()):
                    image_url = url
                    break
            
            # Special case handling
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
            
            # Cache for 1 year (circuit info rarely changes)
            self.cache_repo.set(cache_key, circuit_data, int(timedelta(days=365).total_seconds()))
            
            return circuit_data
            
        except Exception as e:
            logger.error(f"Error getting circuit info: {e}")
            raise


# Global schedule service instance
schedule_service = ScheduleService() 