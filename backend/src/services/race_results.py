from typing import List, Optional
from datetime import datetime, timedelta
import pandas as pd
import logging
from repositories.cache import cache_repo
from repositories.f1_data import f1_data_repo
from models.race_results import (
    RaceResult, QualifyingResult, PracticeResult, SprintResult,
    RaceResultsResponse, QualifyingResultsResponse, PracticeResultsResponse,
    SprintResultsResponse, RaceSummaryResponse, RaceHighlightsResponse,
    RaceInfo, SessionAvailable, RaceHighlights, RaceWinner, PolePosition, FastestLap
)
from utils.time_utils import format_lap_time, format_race_time, format_gap_time
from utils.constants import SESSION_TYPES
from config.settings import settings

logger = logging.getLogger(__name__)


class RaceResultsService:
    """Service for handling F1 race results business logic"""
    
    def __init__(self):
        self.cache_repo = cache_repo
        self.f1_data_repo = f1_data_repo
    
    def get_race_results(self, year: int, round_num: int) -> RaceResultsResponse:
        """Get complete race results data"""
        
        # Validate inputs
        if not self.f1_data_repo.validate_year(year):
            raise ValueError(f"Invalid year: {year}")
        
        cache_key = f"race_results_{year}_{round_num}"
        cached_data = self.cache_repo.get(cache_key)
        
        if cached_data:
            logger.info(f"Race results cache hit for {year} round {round_num}")
            return RaceResultsResponse(
                race_info=cached_data["race_info"],
                results=cached_data["results"],
                cache_info=self.cache_repo.get_cache_info(cache_key)
            )
        
        try:
            logger.info(f"Fetching race results for {year} round {round_num}")
            
            # Get race event info
            schedule = self.f1_data_repo.get_event_schedule(year)
            race_info_df = schedule[schedule['RoundNumber'] == round_num].iloc[0]
            
            # Get race session
            session = self.f1_data_repo.get_session(year, round_num, 'R')
            session = self.f1_data_repo.load_session_data(session, laps=True, telemetry=False, weather=False, messages=False)
            
            # Calculate lap counts for each driver
            lap_counts = {}
            if session.laps is not None and not session.laps.empty:
                lap_counts = session.laps.groupby('Driver')['LapNumber'].max().to_dict()
            
            results = []
            
            # Process official results data
            if not session.results.empty:
                for _, driver in session.results.iterrows():
                    position = int(driver['Position']) if pd.notna(driver['Position']) else None
                    driver_time = driver.get('Time')
                    
                    # Handle time display: winner shows full time, others show full time + gap
                    formatted_time = None
                    gap = None
                    
                    if position == 1 and pd.notna(driver_time):
                        # Winner shows full race time
                        formatted_time = self.f1_data_repo.format_race_time(driver_time)
                        gap = None
                    elif position and position > 1 and pd.notna(driver_time):
                        # Other drivers: calculate full time and gap
                        gap_seconds = driver_time.total_seconds()
                        gap = format_gap_time(gap_seconds)
                        
                        # Get winner's full time to calculate other drivers' full time
                        first_driver = session.results.iloc[0]
                        first_time = first_driver.get('Time')
                        if pd.notna(first_time):
                            # Other drivers' full time = winner time + time gap
                            full_time = first_time + driver_time
                            formatted_time = self.f1_data_repo.format_race_time(full_time)
                    
                    # Handle laps data
                    driver_abbr = driver.get('Abbreviation')
                    laps_value = lap_counts.get(driver_abbr, 0)
                    
                    # Handle status data
                    status = driver.get('Status', 'Unknown')
                    if pd.isna(status) or status == '':
                        # If no status info, infer from position and laps
                        if position and position <= 20:
                            status = "Finished"
                        else:
                            status = "DNF"
                    
                    results.append(RaceResult(
                        position=position,
                        driver=driver['FullName'],
                        team=driver['TeamName'],
                        time=formatted_time,
                        gap=gap,
                        points=float(driver['Points']) if pd.notna(driver['Points']) else 0,
                        status=status,
                        laps=int(laps_value) if pd.notna(laps_value) else 0
                    ))
            
            # Build race info
            race_info = RaceInfo(
                round=int(race_info_df['RoundNumber']),
                race_name=race_info_df['EventName'],
                location=race_info_df['Location'],
                country=race_info_df['Country'],
                date=race_info_df['EventDate'].strftime('%Y-%m-%d')
            )
            
            # Prepare response data for caching
            response_data = {
                "race_info": race_info.dict(),
                "results": [result.dict() for result in results]
            }
            
            # Cache completed races for 30 days (they don't change)
            self.cache_repo.set(cache_key, response_data, settings.cache_ttl_race_results)
            
            return RaceResultsResponse(
                race_info=race_info,
                results=results,
                cache_info=self.cache_repo.get_cache_info(cache_key)
            )
            
        except Exception as e:
            logger.error(f"Error getting race results for {year} round {round_num}: {e}")
            raise
    
    def get_qualifying_results(self, year: int, round_num: int) -> QualifyingResultsResponse:
        """Get qualifying results for a specific race"""
        
        cache_key = f"race_qualifying_{year}_{round_num}"
        cached_data = self.cache_repo.get(cache_key)
        
        if cached_data:
            logger.info(f"Qualifying results cache hit for {year} round {round_num}")
            return QualifyingResultsResponse(
                data=cached_data,
                cache_info=self.cache_repo.get_cache_info(cache_key)
            )
        
        try:
            logger.info(f"Fetching qualifying results for {year} round {round_num}")
            
            session = self.f1_data_repo.get_session(year, round_num, 'Q')
            session = self.f1_data_repo.load_session_data(session, laps=True, telemetry=False, weather=False, messages=False)
            
            # Calculate lap counts for each driver
            lap_counts = {}
            if session.laps is not None and not session.laps.empty:
                lap_counts = session.laps.groupby('Driver')['LapNumber'].max().to_dict()
            
            qualifying_results = []
            for _, driver in session.results.iterrows():
                driver_abbr = driver.get('Abbreviation')
                laps_value = lap_counts.get(driver_abbr, 0)
                
                qualifying_results.append(QualifyingResult(
                    position=int(driver['Position']) if pd.notna(driver['Position']) else None,
                    driver=driver['FullName'],
                    team=driver['TeamName'],
                    q1=self.f1_data_repo.format_lap_time(driver.get('Q1')),
                    q2=self.f1_data_repo.format_lap_time(driver.get('Q2')),
                    q3=self.f1_data_repo.format_lap_time(driver.get('Q3')),
                    laps=int(laps_value) if pd.notna(laps_value) else 0
                ))
            
            # Transform to dict for caching
            results_data = [result.dict() for result in qualifying_results]
            
            # Cache for 30 days
            self.cache_repo.set(cache_key, results_data, settings.cache_ttl_race_results)
            
            return QualifyingResultsResponse(
                data=qualifying_results,
                cache_info=self.cache_repo.get_cache_info(cache_key)
            )
            
        except Exception as e:
            logger.error(f"Error getting qualifying results for {year} round {round_num}: {e}")
            raise
    
    def get_practice_results(self, year: int, round_num: int, session_type: str = "FP1") -> PracticeResultsResponse:
        """Get practice session results (FP1, FP2, FP3, SQ, S)"""
        
        cache_key = f"race_practice_{year}_{round_num}_{session_type}"
        cached_data = self.cache_repo.get(cache_key)
        
        if cached_data:
            logger.info(f"Practice results cache hit for {year} round {round_num} {session_type}")
            return PracticeResultsResponse(
                data=cached_data,
                session=session_type,
                cache_info=self.cache_repo.get_cache_info(cache_key)
            )
        
        try:
            logger.info(f"Fetching practice results for {year} round {round_num} {session_type}")
            
            # Get session
            session_obj = self.f1_data_repo.get_session(year, round_num, session_type)
            if session_obj is None:
                return PracticeResultsResponse(data=[], session=session_type)
            
            session_obj = self.f1_data_repo.load_session_data(session_obj, laps=True)
            results = []
            
            # Determine session type
            is_sprint_session = session_type in ['S', 'Sprint']
            
            if is_sprint_session:
                # Sprint session: similar to race, has Position, Time etc.
                if hasattr(session_obj, 'results') and session_obj.results is not None and not session_obj.results.empty:
                    # Calculate lap counts for each driver
                    lap_counts = {}
                    if session_obj.laps is not None and not session_obj.laps.empty:
                        lap_counts = session_obj.laps.groupby('Driver')['LapNumber'].max().to_dict()
                    
                    for _, driver in session_obj.results.iterrows():
                        position = int(driver['Position']) if pd.notna(driver['Position']) else None
                        driver_time = driver.get('Time')
                        
                        # Handle time display: winner shows full time, others show full time + gap
                        formatted_time = None
                        gap = None
                        
                        if position == 1 and pd.notna(driver_time):
                            # Winner shows full sprint time
                            formatted_time = self.f1_data_repo.format_race_time(driver_time)
                            gap = None
                        elif position and position > 1 and pd.notna(driver_time):
                            # Other drivers: calculate full time and gap
                            gap_seconds = driver_time.total_seconds()
                            gap = format_gap_time(gap_seconds)
                            
                            # Get winner's full time to calculate other drivers' full time
                            first_driver = session_obj.results.iloc[0]
                            first_time = first_driver.get('Time')
                            if pd.notna(first_time):
                                # Other drivers' full time = winner time + time gap
                                full_time = first_time + driver_time
                                formatted_time = self.f1_data_repo.format_race_time(full_time)
                        
                        # Handle laps data
                        driver_abbr = driver.get('Abbreviation')
                        laps_value = lap_counts.get(driver_abbr, 0)
                        
                        # Handle status data
                        status = driver.get('Status', 'Unknown')
                        if pd.isna(status) or status == '':
                            if position and position <= 20:
                                status = "Finished"
                            else:
                                status = "DNF"
                        
                        results.append(SprintResult(
                            position=position,
                            driver=driver['FullName'],
                            team=driver['TeamName'],
                            time=formatted_time,
                            gap=gap,
                            points=float(driver['Points']) if pd.notna(driver['Points']) else 0,
                            status=status,
                            laps=int(laps_value) if pd.notna(laps_value) else 0
                        ))
                
                # Transform to dict for caching
                results_data = [result.dict() for result in results]
                
                # Cache results
                self.cache_repo.set(cache_key, results_data, settings.cache_ttl_race_results)
                
                return SprintResultsResponse(
                    data=results,
                    cache_info=self.cache_repo.get_cache_info(cache_key)
                )
            else:
                # Practice and Sprint Qualifying sessions: show fastest lap times and gaps
                # Calculate lap counts and best times for each driver
                lap_counts = {}
                best_times = {}
                fastest_overall = None
                
                if session_obj.laps is not None and not session_obj.laps.empty:
                    lap_counts = session_obj.laps.groupby('Driver')['LapNumber'].max().to_dict()
                    
                    # Calculate each driver's fastest lap time
                    valid_laps = session_obj.laps[session_obj.laps['LapTime'].notna()]
                    if not valid_laps.empty:
                        best_times = valid_laps.groupby('Driver')['LapTime'].min().to_dict()
                        # Find overall fastest lap time
                        fastest_overall = valid_laps['LapTime'].min()
                
                if hasattr(session_obj, 'results') and session_obj.results is not None and not session_obj.results.empty:
                    for idx, (_, driver) in enumerate(session_obj.results.iterrows(), 1):
                        # Practice and Sprint Qualifying sessions don't have Position field, use index as ranking
                        position = idx
                        
                        driver_abbr = driver.get('Abbreviation')
                        laps_value = lap_counts.get(driver_abbr, 0)
                        
                        # Get driver's fastest lap time
                        best_time = best_times.get(driver_abbr)
                        best_time_str = self.f1_data_repo.format_lap_time(best_time) if best_time and pd.notna(best_time) else None
                        
                        # Calculate gap to fastest overall
                        gap_to_fastest = None
                        if best_time and pd.notna(best_time) and fastest_overall and pd.notna(fastest_overall):
                            if best_time != fastest_overall:
                                gap_seconds = (best_time - fastest_overall).total_seconds()
                                if gap_seconds > 0:
                                    gap_to_fastest = format_gap_time(gap_seconds)
                        
                        results.append(PracticeResult(
                            position=position,
                            driver=str(driver.get('FullName', driver.get('Driver', 'Unknown'))),
                            team=str(driver.get('TeamName', driver.get('Team', 'Unknown'))),
                            time=best_time_str,      # Best Time shown in time field
                            gap=gap_to_fastest,      # Gap to Fastest shown in gap field
                            laps=int(laps_value) if pd.notna(laps_value) else 0
                        ))
                
                # Transform to dict for caching
                results_data = [result.dict() for result in results]
                
                # Cache results
                self.cache_repo.set(cache_key, results_data, settings.cache_ttl_race_results)
                
                return PracticeResultsResponse(
                    data=results,
                    session=session_type,
                    cache_info=self.cache_repo.get_cache_info(cache_key)
                )
            
        except Exception as e:
            logger.error(f"Error getting practice results for {year} round {round_num} session {session_type}: {e}")
            raise
    
    def get_race_summary(self, year: int, round_num: int) -> RaceSummaryResponse:
        """Get race weekend summary of all available sessions"""
        
        cache_key = f"race_summary_{year}_{round_num}"
        cached_data = self.cache_repo.get(cache_key)
        
        if cached_data:
            logger.info(f"Race summary cache hit for {year} round {round_num}")
            return RaceSummaryResponse(
                race_info=cached_data["race_info"],
                sessions_available=cached_data["sessions_available"],
                cache_info=self.cache_repo.get_cache_info(cache_key)
            )
        
        try:
            logger.info(f"Fetching race summary for {year} round {round_num}")
            
            # Get basic race information
            schedule = self.f1_data_repo.get_event_schedule(year)
            race_info_df = schedule[schedule['RoundNumber'] == round_num].iloc[0]
            
            race_info = RaceInfo(
                round=int(race_info_df['RoundNumber']),
                race_name=race_info_df['EventName'],
                location=race_info_df['Location'],
                country=race_info_df['Country'],
                date=race_info_df['EventDate'].strftime('%Y-%m-%d')
            )
            
            sessions_available = []
            
            # Check all possible session types, including Sprint weekend sessions
            all_possible_sessions = ['FP1', 'FP2', 'FP3', 'SQ', 'S', 'Q', 'R']
            
            for session_type in all_possible_sessions:
                try:
                    session = self.f1_data_repo.get_session(year, round_num, session_type)
                    if session is not None:
                        # Try to check if session has data
                        try:
                            session = self.f1_data_repo.load_session_data(session, laps=False, telemetry=False, weather=False, messages=False)
                            has_results = hasattr(session, 'results') and session.results is not None
                            if has_results and not session.results.empty:
                                sessions_available.append(SessionAvailable(
                                    session=session_type,
                                    name=SESSION_TYPES.get(session_type, session_type),
                                    key=SESSION_TYPES.get(session_type, session_type).replace(' ', '_').lower()
                                ))
                        except Exception:
                            # Load failure usually means the session wasn't actually held or data not available yet, skip
                            continue
                except:
                    continue
            
            # Prepare response data for caching
            response_data = {
                "race_info": race_info.dict(),
                "sessions_available": [session.dict() for session in sessions_available]
            }
            
            # Cache for 1 week
            self.cache_repo.set(cache_key, response_data, int(timedelta(weeks=1).total_seconds()))
            
            return RaceSummaryResponse(
                race_info=race_info,
                sessions_available=sessions_available,
                cache_info=self.cache_repo.get_cache_info(cache_key)
            )
            
        except Exception as e:
            logger.error(f"Error getting race summary for {year} round {round_num}: {e}")
            raise
    
    def get_race_highlights(self, year: int, round_num: int) -> RaceHighlightsResponse:
        """Get race highlights data: Race winner, Pole Position, Fastest lap"""
        
        cache_key = f"race_highlights_{year}_{round_num}"
        cached_data = self.cache_repo.get(cache_key)
        
        if cached_data:
            logger.info(f"Race highlights cache hit for {year} round {round_num}")
            return RaceHighlightsResponse(
                data=cached_data,
                cache_info=self.cache_repo.get_cache_info(cache_key)
            )
        
        try:
            logger.info(f"Fetching race highlights for {year} round {round_num}")
            
            highlights = RaceHighlights(
                race_winner=None,
                pole_position=None, 
                fastest_lap=None
            )
            
            # 1. Get Race Winner
            try:
                race_session = self.f1_data_repo.get_session(year, round_num, 'R')
                race_session = self.f1_data_repo.load_session_data(race_session, laps=True, telemetry=False, weather=False, messages=False)
                
                if not race_session.results.empty:
                    winner = race_session.results.iloc[0]  # First place
                    winner_time = winner.get('Time')
                    formatted_time = self.f1_data_repo.format_race_time(winner_time) if pd.notna(winner_time) else None
                    
                    highlights.race_winner = RaceWinner(
                        driver_name=winner['FullName'],
                        race_time=formatted_time
                    )
            except Exception as e:
                logger.warning(f"Error getting race winner: {e}")
            
            # 2. Get Pole Position
            try:
                qualifying_session = self.f1_data_repo.get_session(year, round_num, 'Q')
                qualifying_session = self.f1_data_repo.load_session_data(qualifying_session, laps=True, telemetry=False, weather=False, messages=False)
                
                if not qualifying_session.results.empty:
                    pole_sitter = qualifying_session.results.iloc[0]  # Qualifying first place
                    # Get fastest qualifying time (prioritize Q3, then Q2, then Q1)
                    pole_time = None
                    for q_session in ['Q3', 'Q2', 'Q1']:
                        time_val = pole_sitter.get(q_session)
                        if pd.notna(time_val):
                            pole_time = time_val
                            break
                    
                    formatted_time = self.f1_data_repo.format_lap_time(pole_time) if pole_time else None
                    
                    highlights.pole_position = PolePosition(
                        driver_name=pole_sitter['FullName'],
                        qualifying_time=formatted_time
                    )
            except Exception as e:
                logger.warning(f"Error getting pole position: {e}")
            
            # 3. Get Fastest Lap
            try:
                race_session = self.f1_data_repo.get_session(year, round_num, 'R')
                race_session = self.f1_data_repo.load_session_data(race_session, laps=True, telemetry=False, weather=False, messages=False)
                
                if race_session.laps is not None and not race_session.laps.empty:
                    # Find fastest lap
                    valid_laps = race_session.laps[race_session.laps['LapTime'].notna()]
                    if not valid_laps.empty:
                        fastest_lap = valid_laps.loc[valid_laps['LapTime'].idxmin()]
                        
                        highlights.fastest_lap = FastestLap(
                            driver_name=fastest_lap['Driver'],  # This is abbreviation, need to convert to full name
                            lap_number=int(fastest_lap['LapNumber']),
                            lap_time=self.f1_data_repo.format_lap_time(fastest_lap['LapTime'])
                        )
                        
                        # Try to get driver full name
                        try:
                            driver_info = race_session.results[race_session.results['Abbreviation'] == fastest_lap['Driver']]
                            if not driver_info.empty:
                                highlights.fastest_lap.driver_name = driver_info.iloc[0]['FullName']
                        except:
                            pass  # If getting full name fails, keep abbreviation
            except Exception as e:
                logger.warning(f"Error getting fastest lap: {e}")
            
            # Cache for 30 days (race results don't change)
            self.cache_repo.set(cache_key, highlights.dict(), settings.cache_ttl_race_results)
            
            return RaceHighlightsResponse(
                data=highlights,
                cache_info=self.cache_repo.get_cache_info(cache_key)
            )
            
        except Exception as e:
            logger.error(f"Error getting race highlights for {year} round {round_num}: {e}")
            raise


# Global race results service instance
race_results_service = RaceResultsService() 