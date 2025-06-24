from pydantic import BaseModel, Field
from typing import List, Optional
from .base import BaseResponse, CacheInfo


class RaceResult(BaseModel):
    """Single race result entry"""
    position: Optional[int] = Field(description="Final position (null if DNF/DNS)")
    driver: str = Field(description="Driver full name")
    team: str = Field(description="Team/Constructor name")
    time: Optional[str] = Field(description="Race time or completion time")
    gap: Optional[str] = Field(description="Gap to winner (e.g., +5.123s)")
    points: float = Field(description="Points awarded")
    status: str = Field(description="Race status (Finished, DNF, etc.)")
    laps: int = Field(description="Number of laps completed")


class QualifyingResult(BaseModel):
    """Single qualifying result entry"""
    position: Optional[int] = Field(description="Qualifying position")
    driver: str = Field(description="Driver full name")
    team: str = Field(description="Team/Constructor name")
    q1: Optional[str] = Field(description="Q1 time")
    q2: Optional[str] = Field(description="Q2 time")
    q3: Optional[str] = Field(description="Q3 time")
    laps: int = Field(description="Number of laps completed")


class PracticeResult(BaseModel):
    """Single practice session result entry"""
    position: int = Field(description="Session position")
    driver: str = Field(description="Driver full name")
    team: str = Field(description="Team/Constructor name")
    time: Optional[str] = Field(description="Best lap time")
    gap: Optional[str] = Field(description="Gap to fastest (e.g., +0.123s)")
    laps: int = Field(description="Number of laps completed")


class SprintResult(BaseModel):
    """Single sprint session result entry"""
    position: Optional[int] = Field(description="Final position (null if DNF/DNS)")
    driver: str = Field(description="Driver full name")
    team: str = Field(description="Team/Constructor name")
    time: Optional[str] = Field(description="Sprint time or completion time")
    gap: Optional[str] = Field(description="Gap to winner (e.g., +5.123s)")
    points: float = Field(description="Points awarded")
    status: str = Field(description="Sprint status (Finished, DNF, etc.)")
    laps: int = Field(description="Number of laps completed")


class SessionAvailable(BaseModel):
    """Available session information"""
    session: str = Field(description="Session code (FP1, Q, R, etc.)")
    name: str = Field(description="Session display name")
    key: str = Field(description="Session key for API calls")


class RaceHighlight(BaseModel):
    """Race highlight entry"""
    driver_name: str = Field(description="Driver full name")


class RaceWinner(RaceHighlight):
    """Race winner information"""
    race_time: Optional[str] = Field(description="Total race time")


class PolePosition(RaceHighlight):
    """Pole position information"""
    qualifying_time: Optional[str] = Field(description="Pole position qualifying time")


class FastestLap(RaceHighlight):
    """Fastest lap information"""
    lap_number: int = Field(description="Lap number when fastest lap was set")
    lap_time: Optional[str] = Field(description="Fastest lap time")


class RaceHighlights(BaseModel):
    """Race highlights collection"""
    race_winner: Optional[RaceWinner] = Field(description="Race winner information")
    pole_position: Optional[PolePosition] = Field(description="Pole position information")
    fastest_lap: Optional[FastestLap] = Field(description="Fastest lap information")


class RaceInfo(BaseModel):
    """Race event information"""
    round: int = Field(description="Race round number")
    race_name: str = Field(description="Official race name")
    location: str = Field(description="Circuit location")
    country: str = Field(description="Country")
    date: str = Field(description="Race date (YYYY-MM-DD)")


class RaceResultsResponse(BaseResponse):
    """Race results response model"""
    race_info: RaceInfo = Field(description="Race information")
    results: List[RaceResult] = Field(description="Race results")
    cache_info: Optional[CacheInfo] = Field(default=None, description="Cache information")


class QualifyingResultsResponse(BaseResponse):
    """Qualifying results response model"""
    data: List[QualifyingResult] = Field(description="Qualifying results")
    cache_info: Optional[CacheInfo] = Field(default=None, description="Cache information")


class PracticeResultsResponse(BaseResponse):
    """Practice results response model"""
    data: List[PracticeResult] = Field(description="Practice session results")
    session: str = Field(description="Session type (FP1, FP2, etc.)")
    cache_info: Optional[CacheInfo] = Field(default=None, description="Cache information")


class SprintResultsResponse(BaseResponse):
    """Sprint results response model"""
    data: List[SprintResult] = Field(description="Sprint session results")
    cache_info: Optional[CacheInfo] = Field(default=None, description="Cache information")


class RaceSummaryResponse(BaseResponse):
    """Race summary response model"""
    race_info: RaceInfo = Field(description="Race information")
    sessions_available: List[SessionAvailable] = Field(description="Available sessions")
    cache_info: Optional[CacheInfo] = Field(default=None, description="Cache information")


class RaceHighlightsResponse(BaseResponse):
    """Race highlights response model"""
    data: RaceHighlights = Field(description="Race highlights")
    cache_info: Optional[CacheInfo] = Field(default=None, description="Cache information") 