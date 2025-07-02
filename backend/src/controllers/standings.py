from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
import logging
from services.standings import standings_service
from models.standings import DriverStandingsResponse, ConstructorStandingsResponse
from models.base import ErrorResponse

logger = logging.getLogger(__name__)

# Create router for standings endpoints
router = APIRouter(
    prefix="/standings",
    tags=["standings"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)


class StandingsController:
    """Controller for handling standings HTTP requests"""
    
    def __init__(self):
        self.standings_service = standings_service
    
    async def get_driver_standings(
        self, 
        year: Optional[int] = Query(None, description="Championship year"),
        round: Optional[int] = Query(None, description="Round number", alias="round")
    ) -> DriverStandingsResponse:
        """
        Get driver championship standings
        
        Args:
            year: Championship year (defaults to current year)
            round: Round number (defaults to latest round)
            
        Returns:
            Driver standings data with metadata and cache info
            
        Raises:
            HTTPException: For invalid parameters or service errors
        """
        try:
            logger.info(f"Driver standings request: year={year}, round={round}")
            return self.standings_service.get_driver_standings(year, round)
            
        except ValueError as e:
            logger.warning(f"Invalid parameters for driver standings: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error getting driver standings: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_constructor_standings(
        self, 
        year: Optional[int] = Query(None, description="Championship year"),
        round: Optional[int] = Query(None, description="Round number", alias="round")
    ) -> ConstructorStandingsResponse:
        """
        Get constructor championship standings
        
        Args:
            year: Championship year (defaults to current year)
            round: Round number (defaults to latest round)
            
        Returns:
            Constructor standings data with metadata and cache info
            
        Raises:
            HTTPException: For invalid parameters or service errors
        """
        try:
            logger.info(f"Constructor standings request: year={year}, round={round}")
            return self.standings_service.get_constructor_standings(year, round)
            
        except ValueError as e:
            logger.warning(f"Invalid parameters for constructor standings: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error getting constructor standings: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")


# Create controller instance
standings_controller = StandingsController()

# Register routes
@router.get(
    "/drivers", 
    response_model=DriverStandingsResponse,
    summary="Get driver standings",
    description="Get F1 driver championship standings for a specific year and round"
)
async def get_driver_standings(
    year: Optional[int] = Query(None, description="Championship year"),
    round: Optional[int] = Query(None, description="Round number", alias="round")
):
    return await standings_controller.get_driver_standings(year, round)


@router.get(
    "/constructors", 
    response_model=ConstructorStandingsResponse,
    summary="Get constructor standings",
    description="Get F1 constructor championship standings for a specific year and round"
)
async def get_constructor_standings(
    year: Optional[int] = Query(None, description="Championship year"),
    round: Optional[int] = Query(None, description="Round number", alias="round")
):
    return await standings_controller.get_constructor_standings(year, round) 