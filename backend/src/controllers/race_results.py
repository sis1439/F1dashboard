from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging
from services.race_results import race_results_service
from models.race_results import (
    RaceResultsResponse, QualifyingResultsResponse, PracticeResultsResponse,
    SprintResultsResponse, RaceSummaryResponse, RaceHighlightsResponse
)
from models.base import ErrorResponse

logger = logging.getLogger(__name__)

# Create router for race results endpoints
router = APIRouter(
    prefix="/race-results",
    tags=["race-results"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)


class RaceResultsController:
    """Controller for handling race results HTTP requests"""
    
    def __init__(self):
        self.race_results_service = race_results_service
    
    async def get_race_results(
        self, 
        year: int = Query(..., description="Championship year"),
        round: int = Query(..., description="Round number", alias="round")
    ) -> RaceResultsResponse:
        """
        Get race results
        
        Args:
            year: Championship year
            round: Round number
            
        Returns:
            Race results data with metadata and cache info
            
        Raises:
            HTTPException: For invalid parameters or service errors
        """
        try:
            logger.info(f"Race results request: year={year}, round={round}")
            return self.race_results_service.get_race_results(year, round)
            
        except ValueError as e:
            logger.warning(f"Invalid parameters for race results: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error getting race results: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_qualifying_results(
        self, 
        year: int = Query(..., description="Championship year"),
        round: int = Query(..., description="Round number", alias="round")
    ) -> QualifyingResultsResponse:
        """
        Get qualifying results
        
        Args:
            year: Championship year
            round: Round number
            
        Returns:
            Qualifying results data with cache info
            
        Raises:
            HTTPException: For invalid parameters or service errors
        """
        try:
            logger.info(f"Qualifying results request: year={year}, round={round}")
            return self.race_results_service.get_qualifying_results(year, round)
            
        except ValueError as e:
            logger.warning(f"Invalid parameters for qualifying results: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error getting qualifying results: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_practice_results(
        self, 
        year: int = Query(..., description="Championship year"),
        round: int = Query(..., description="Round number", alias="round"),
        session: str = Query("FP1", description="Session type (FP1, FP2, FP3, SQ, S)")
    ) -> PracticeResultsResponse:
        """
        Get practice session results
        
        Args:
            year: Championship year
            round: Round number
            session: Session type (FP1, FP2, FP3, SQ, S)
            
        Returns:
            Practice session results data with cache info
            
        Raises:
            HTTPException: For invalid parameters or service errors
        """
        try:
            logger.info(f"Practice results request: year={year}, round={round}, session={session}")
            return self.race_results_service.get_practice_results(year, round, session)
            
        except ValueError as e:
            logger.warning(f"Invalid parameters for practice results: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error getting practice results: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_race_summary(
        self, 
        year: int = Query(..., description="Championship year"),
        round: int = Query(..., description="Round number", alias="round")
    ) -> RaceSummaryResponse:
        """
        Get race weekend summary
        
        Args:
            year: Championship year
            round: Round number
            
        Returns:
            Race weekend summary with available sessions
            
        Raises:
            HTTPException: For invalid parameters or service errors
        """
        try:
            logger.info(f"Race summary request: year={year}, round={round}")
            return self.race_results_service.get_race_summary(year, round)
            
        except ValueError as e:
            logger.warning(f"Invalid parameters for race summary: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error getting race summary: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_race_highlights(
        self, 
        year: int = Query(..., description="Championship year"),
        round: int = Query(..., description="Round number", alias="round")
    ) -> RaceHighlightsResponse:
        """
        Get race highlights
        
        Args:
            year: Championship year
            round: Round number
            
        Returns:
            Race highlights (winner, pole, fastest lap)
            
        Raises:
            HTTPException: For invalid parameters or service errors
        """
        try:
            logger.info(f"Race highlights request: year={year}, round={round}")
            return self.race_results_service.get_race_highlights(year, round)
            
        except ValueError as e:
            logger.warning(f"Invalid parameters for race highlights: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error getting race highlights: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")


# Create controller instance
race_results_controller = RaceResultsController()

# Register routes
@router.get(
    "/race", 
    response_model=RaceResultsResponse,
    summary="Get race results",
    description="Get F1 race results for a specific year and round"
)
async def get_race_results(
    year: int = Query(..., description="Championship year"),
    round: int = Query(..., description="Round number", alias="round")
):
    return await race_results_controller.get_race_results(year, round)


@router.get(
    "/qualifying", 
    response_model=QualifyingResultsResponse,
    summary="Get qualifying results",
    description="Get F1 qualifying results for a specific year and round"
)
async def get_qualifying_results(
    year: int = Query(..., description="Championship year"),
    round: int = Query(..., description="Round number", alias="round")
):
    return await race_results_controller.get_qualifying_results(year, round)


@router.get(
    "/practice", 
    response_model=PracticeResultsResponse,
    summary="Get practice results",
    description="Get F1 practice session results (FP1, FP2, FP3, SQ, S)"
)
async def get_practice_results(
    year: int = Query(..., description="Championship year"),
    round: int = Query(..., description="Round number", alias="round"),
    session: str = Query("FP1", description="Session type (FP1, FP2, FP3, SQ, S)")
):
    return await race_results_controller.get_practice_results(year, round, session)


@router.get(
    "/summary", 
    response_model=RaceSummaryResponse,
    summary="Get race summary",
    description="Get race weekend summary with available sessions"
)
async def get_race_summary(
    year: int = Query(..., description="Championship year"),
    round: int = Query(..., description="Round number", alias="round")
):
    return await race_results_controller.get_race_summary(year, round)


@router.get(
    "/highlights", 
    response_model=RaceHighlightsResponse,
    summary="Get race highlights",
    description="Get race highlights (winner, pole position, fastest lap)"
)
async def get_race_highlights(
    year: int = Query(..., description="Championship year"),
    round: int = Query(..., description="Round number", alias="round")
):
    return await race_results_controller.get_race_highlights(year, round) 