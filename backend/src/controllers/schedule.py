from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging
from services.schedule import schedule_service
from models.schedule import (
    AvailableYearsResponse, RaceScheduleResponse, NextRaceResponse,
    RaceWeekendScheduleResponse
)
from models.base import ErrorResponse

logger = logging.getLogger(__name__)

# Create router for schedule endpoints
router = APIRouter(
    prefix="/schedule",
    tags=["schedule"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)


class ScheduleController:
    """Controller for handling schedule HTTP requests"""
    
    def __init__(self):
        self.schedule_service = schedule_service
    
    async def get_available_years(self) -> AvailableYearsResponse:
        """
        Get available years for F1 data
        
        Returns:
            Available years list with cache info
            
        Raises:
            HTTPException: For service errors
        """
        try:
            logger.info("Available years request")
            return self.schedule_service.get_available_years()
            
        except Exception as e:
            logger.error(f"Error getting available years: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_race_schedule(
        self, 
        year: Optional[int] = Query(None, description="Championship year")
    ) -> RaceScheduleResponse:
        """
        Get complete season race schedule
        
        Args:
            year: Championship year (defaults to current year)
            
        Returns:
            Race schedule data with cache info
            
        Raises:
            HTTPException: For invalid parameters or service errors
        """
        try:
            logger.info(f"Race schedule request: year={year}")
            return self.schedule_service.get_race_schedule(year)
            
        except ValueError as e:
            logger.warning(f"Invalid parameters for race schedule: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error getting race schedule: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_next_race(
        self, 
        year: Optional[int] = Query(None, description="Championship year")
    ) -> NextRaceResponse:
        """
        Get next race information
        
        Args:
            year: Championship year (defaults to current year)
            
        Returns:
            Next race information
            
        Raises:
            HTTPException: For service errors
        """
        try:
            logger.info(f"Next race request: year={year}")
            return self.schedule_service.get_next_race_info(year)
            
        except Exception as e:
            logger.error(f"Error getting next race: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_race_weekend_schedule(
        self, 
        year: Optional[int] = Query(None, description="Championship year"),
        round: Optional[int] = Query(None, description="Round number", alias="round")
    ) -> RaceWeekendScheduleResponse:
        """
        Get detailed race weekend schedule with all sessions
        
        Args:
            year: Championship year (defaults to current year)
            round: Round number (defaults to next race)
            
        Returns:
            Race weekend schedule with sessions and circuit info
            
        Raises:
            HTTPException: For invalid parameters or service errors
        """
        try:
            logger.info(f"Race weekend schedule request: year={year}, round={round}")
            return self.schedule_service.get_race_weekend_schedule(year, round)
            
        except ValueError as e:
            logger.warning(f"Invalid parameters for race weekend schedule: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error getting race weekend schedule: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_circuit_info(
        self, 
        year: Optional[int] = Query(None, description="Championship year"),
        round: Optional[int] = Query(None, description="Round number", alias="round")
    ) -> dict:
        """
        Get circuit information including image URLs
        
        Args:
            year: Championship year (defaults to current year)
            round: Round number (defaults to next race)
            
        Returns:
            Circuit information with image URL
            
        Raises:
            HTTPException: For invalid parameters or service errors
        """
        try:
            logger.info(f"Circuit info request: year={year}, round={round}")
            return self.schedule_service.get_circuit_info(year, round)
            
        except ValueError as e:
            logger.warning(f"Invalid parameters for circuit info: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error getting circuit info: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")


# Create controller instance
schedule_controller = ScheduleController()

# Register routes
@router.get(
    "/available-years", 
    response_model=AvailableYearsResponse,
    summary="Get available years",
    description="Get list of available years for F1 data"
)
async def get_available_years():
    return await schedule_controller.get_available_years()


@router.get(
    "/race-schedule", 
    response_model=RaceScheduleResponse,
    summary="Get race schedule",
    description="Get complete season race schedule for a specific year"
)
async def get_race_schedule(
    year: Optional[int] = Query(None, description="Championship year")
):
    return await schedule_controller.get_race_schedule(year)


@router.get(
    "/next-race", 
    response_model=NextRaceResponse,
    summary="Get next race",
    description="Get information about the next upcoming race"
)
async def get_next_race(
    year: Optional[int] = Query(None, description="Championship year")
):
    return await schedule_controller.get_next_race(year)


@router.get(
    "/race-weekend-schedule", 
    response_model=RaceWeekendScheduleResponse,
    summary="Get race weekend schedule",
    description="Get detailed race weekend schedule with all sessions"
)
async def get_race_weekend_schedule(
    year: Optional[int] = Query(None, description="Championship year"),
    round: Optional[int] = Query(None, description="Round number", alias="round")
):
    return await schedule_controller.get_race_weekend_schedule(year, round)


@router.get(
    "/circuit-info", 
    summary="Get circuit info",
    description="Get circuit information including image URLs"
)
async def get_circuit_info(
    year: Optional[int] = Query(None, description="Championship year"),
    round: Optional[int] = Query(None, description="Round number", alias="round")
):
    return await schedule_controller.get_circuit_info(year, round) 