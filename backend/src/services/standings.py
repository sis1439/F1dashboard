from typing import List, Optional
from datetime import datetime
import logging
from repositories.cache import cache_repo
from repositories.f1_data import f1_data_repo
from models.standings import (
    DriverStanding, ConstructorStanding, 
    DriverStandingsResponse, ConstructorStandingsResponse,
    StandingsMetadata
)
from config.settings import settings

logger = logging.getLogger(__name__)


class StandingsService:
    """Service for handling F1 standings business logic"""
    
    def __init__(self):
        self.cache_repo = cache_repo
        self.f1_data_repo = f1_data_repo
    
    def get_driver_standings(self, year: Optional[int] = None, round_num: Optional[int] = None) -> DriverStandingsResponse:
        """Get driver standings with business logic and caching"""
        
        # Set defaults
        if year is None:
            year = datetime.now().year
            
        if round_num is None:
            round_num = self.f1_data_repo.get_latest_round_ergast(year)
        
        # Validate inputs
        if not self.f1_data_repo.validate_year(year):
            raise ValueError(f"Invalid year: {year}")
        
        # Check cache first
        cache_key = f"driver_standings_{year}_{round_num}"
        cached_data = self.cache_repo.get(cache_key)
        
        if cached_data:
            logger.info(f"Driver standings cache hit for {year} round {round_num}")
            return DriverStandingsResponse(
                data=cached_data["data"],
                metadata=cached_data["metadata"],
                cache_info=self.cache_repo.get_cache_info(cache_key)
            )
        
        try:
            # Fetch data from Ergast API
            logger.info(f"Fetching driver standings for {year} round {round_num}")
            data_json = self.f1_data_repo.get_driver_standings_ergast(year, round_num)
            
            # Process the data
            standings_list = data_json.get('MRData', {}).get('StandingsTable', {}).get('StandingsLists', [])
            if not standings_list:
                raise ValueError(f"No standings data found for {year} round {round_num}")
            
            current_standings = standings_list[0].get('DriverStandings', [])[:10]
            
            # Get previous round data for comparison
            prev_points = {}
            prev_positions = {}
            if round_num > 1:
                try:
                    prev_data = self.f1_data_repo.get_driver_standings_ergast(year, round_num - 1)
                    prev_list = prev_data.get('MRData', {}).get('StandingsTable', {}).get('StandingsLists', [])
                    if prev_list:
                        prev_standings = prev_list[0].get('DriverStandings', [])
                        prev_points = {s['Driver']['driverId']: float(s['points']) for s in prev_standings}
                        prev_positions = {s['Driver']['driverId']: int(s['position']) for s in prev_standings}
                except Exception as e:
                    logger.warning(f"Could not fetch previous round data: {e}")
            
            # Transform data to our model
            driver_standings = []
            for standing in current_standings:
                driver = standing.get('Driver', {})
                driver_id = driver.get('driverId', '')
                current_points = float(standing.get('points', 0))
                current_position = int(standing.get('position', 0))
                
                # Calculate changes
                prev_point = prev_points.get(driver_id, 0)
                points_change = current_points - prev_point
                
                prev_position = prev_positions.get(driver_id, current_position)
                evo = prev_position - current_position  # Positive = moved up
                
                driver_standings.append(DriverStanding(
                    pos=current_position,
                    name=f"{driver.get('givenName', '')} {driver.get('familyName', '')}",
                    points=current_points,
                    points_change=points_change,
                    evo=evo
                ))
            
            # Create metadata
            metadata = StandingsMetadata(
                year=year,
                round=round_num,
                race_name=standings_list[0].get('raceName')
            )
            
            # Prepare response data for caching
            response_data = {
                "data": [standing.dict() for standing in driver_standings],
                "metadata": metadata.dict()
            }
            
            # Cache the data
            self.cache_repo.set(cache_key, response_data, settings.cache_ttl_standings)
            
            return DriverStandingsResponse(
                data=driver_standings,
                metadata=metadata,
                cache_info=self.cache_repo.get_cache_info(cache_key)
            )
            
        except Exception as e:
            logger.error(f"Error fetching driver standings: {e}")
            raise
    
    def get_constructor_standings(self, year: Optional[int] = None, round_num: Optional[int] = None) -> ConstructorStandingsResponse:
        """Get constructor standings with business logic and caching"""
        
        # Set defaults
        if year is None:
            year = datetime.now().year
            
        if round_num is None:
            round_num = self.f1_data_repo.get_latest_round_ergast(year)
        
        # Validate inputs
        if not self.f1_data_repo.validate_year(year):
            raise ValueError(f"Invalid year: {year}")
        
        # Check cache first
        cache_key = f"constructor_standings_{year}_{round_num}"
        cached_data = self.cache_repo.get(cache_key)
        
        if cached_data:
            logger.info(f"Constructor standings cache hit for {year} round {round_num}")
            return ConstructorStandingsResponse(
                data=cached_data["data"],
                metadata=cached_data["metadata"],
                cache_info=self.cache_repo.get_cache_info(cache_key)
            )
        
        try:
            # Fetch data from Ergast API
            logger.info(f"Fetching constructor standings for {year} round {round_num}")
            data_json = self.f1_data_repo.get_constructor_standings_ergast(year, round_num)
            
            # Process the data
            standings_list = data_json.get('MRData', {}).get('StandingsTable', {}).get('StandingsLists', [])
            if not standings_list:
                raise ValueError(f"No constructor standings data found for {year} round {round_num}")
            
            current_standings = standings_list[0].get('ConstructorStandings', [])[:10]
            
            # Get previous round data for comparison
            prev_points = {}
            prev_positions = {}
            if round_num > 1:
                try:
                    prev_data = self.f1_data_repo.get_constructor_standings_ergast(year, round_num - 1)
                    prev_list = prev_data.get('MRData', {}).get('StandingsTable', {}).get('StandingsLists', [])
                    if prev_list:
                        prev_standings = prev_list[0].get('ConstructorStandings', [])
                        prev_points = {s['Constructor']['constructorId']: float(s['points']) for s in prev_standings}
                        prev_positions = {s['Constructor']['constructorId']: int(s['position']) for s in prev_standings}
                except Exception as e:
                    logger.warning(f"Could not fetch previous round data: {e}")
            
            # Transform data to our model
            constructor_standings = []
            for standing in current_standings:
                constructor = standing.get('Constructor', {})
                constructor_id = constructor.get('constructorId', '')
                current_points = float(standing.get('points', 0))
                current_position = int(standing.get('position', 0))
                
                # Calculate changes
                prev_point = prev_points.get(constructor_id, 0)
                points_change = current_points - prev_point
                
                prev_position = prev_positions.get(constructor_id, current_position)
                evo = prev_position - current_position  # Positive = moved up
                
                constructor_standings.append(ConstructorStanding(
                    pos=current_position,
                    name=constructor.get('name', ''),
                    points=current_points,
                    points_change=points_change,
                    evo=evo
                ))
            
            # Create metadata
            metadata = StandingsMetadata(
                year=year,
                round=round_num,
                race_name=standings_list[0].get('raceName')
            )
            
            # Prepare response data for caching
            response_data = {
                "data": [standing.dict() for standing in constructor_standings],
                "metadata": metadata.dict()
            }
            
            # Cache the data
            self.cache_repo.set(cache_key, response_data, settings.cache_ttl_standings)
            
            return ConstructorStandingsResponse(
                data=constructor_standings,
                metadata=metadata,
                cache_info=self.cache_repo.get_cache_info(cache_key)
            )
            
        except Exception as e:
            logger.error(f"Error fetching constructor standings: {e}")
            raise


# Global standings service instance
standings_service = StandingsService() 