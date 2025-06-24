from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from .base import BaseResponse, CacheInfo


class RaceScheduleItem(BaseModel):
    """Single race in the schedule"""
    round: int = Field(description="Race round number")
    race_name: str = Field(description="Official race name")
    location: str = Field(description="Circuit location")
    country: str = Field(description="Country")
    date: str = Field(description="Race date (YYYY-MM-DD)")
    format: str = Field(default="Conventional", description="Race weekend format")


class SessionInfo(BaseModel):
    """Session information model"""
    name: str = Field(description="Session name (e.g., Practice 1, Qualifying)")
    code: str = Field(description="Session code (e.g., FP1, Q, R)")
    date: str = Field(description="Session date (YYYY-MM-DD)")
    time: str = Field(description="Session time (HH:MM)")
    datetime: str = Field(description="Full datetime in ISO format")
    end_datetime: str = Field(description="Session end datetime in ISO format")
    end_time: str = Field(description="Session end time (HH:MM)")
    status: str = Field(description="Session status: upcoming, live, completed")
    duration_minutes: int = Field(description="Session duration in minutes")


class CircuitInfo(BaseModel):
    """Circuit information model"""
    name: str = Field(description="Circuit name")
    location: str = Field(description="Circuit location")
    country: str = Field(description="Country")


class RaceInfo(BaseModel):
    """Race weekend information"""
    round: int = Field(description="Race round number")
    race_name: str = Field(description="Official race name")
    location: str = Field(description="Circuit location")
    country: str = Field(description="Country")
    date: str = Field(description="Race date (YYYY-MM-DD)")
    official_name: str = Field(description="Official event name")


class NextRaceInfo(BaseModel):
    """Next race information"""
    race_name: str = Field(description="Next race name")
    date: str = Field(description="Race date (YYYY-MM-DD)")
    location: str = Field(description="Circuit location")
    country: str = Field(description="Country")


class AvailableYearsResponse(BaseResponse):
    """Available years response model"""
    data: List[int] = Field(description="List of available years")


class RaceScheduleResponse(BaseResponse):
    """Race schedule response model"""
    data: List[RaceScheduleItem] = Field(description="List of races in the schedule")
    year: int = Field(description="Championship year")
    cache_info: Optional[CacheInfo] = Field(default=None, description="Cache information")


class NextRaceResponse(BaseResponse):
    """Next race response model"""
    data: NextRaceInfo = Field(description="Next race information")


class RaceWeekendScheduleResponse(BaseResponse):
    """Race weekend schedule response model"""
    race_info: RaceInfo = Field(description="Race weekend information")
    sessions: List[SessionInfo] = Field(description="List of sessions")
    circuit: CircuitInfo = Field(description="Circuit information")
    cache_info: Optional[CacheInfo] = Field(default=None, description="Cache information") 