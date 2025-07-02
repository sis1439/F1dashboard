from pydantic import BaseModel, Field
from typing import List, Optional
from .base import BaseResponse, CacheInfo


class DriverStanding(BaseModel):
    """Driver standing data model"""
    pos: int = Field(description="Current position in championship")
    name: str = Field(description="Driver full name")
    points: float = Field(description="Total championship points")
    points_change: float = Field(default=0.0, description="Points change from previous round")
    evo: int = Field(default=0, description="Position change from previous round (positive = up)")


class ConstructorStanding(BaseModel):
    """Constructor standing data model"""
    pos: int = Field(description="Current position in championship")
    name: str = Field(description="Constructor/Team name")
    points: float = Field(description="Total championship points")
    points_change: float = Field(default=0.0, description="Points change from previous round")
    evo: int = Field(default=0, description="Position change from previous round (positive = up)")


class StandingsMetadata(BaseModel):
    """Standings metadata"""
    year: int = Field(description="Championship year")
    round: int = Field(description="Round number")
    race_name: Optional[str] = Field(default=None, description="Latest race name")


class DriverStandingsResponse(BaseResponse):
    """Driver standings response model"""
    data: List[DriverStanding] = Field(description="List of driver standings")
    metadata: StandingsMetadata = Field(description="Standings metadata")
    cache_info: Optional[CacheInfo] = Field(default=None, description="Cache information")


class ConstructorStandingsResponse(BaseResponse):
    """Constructor standings response model"""
    data: List[ConstructorStanding] = Field(description="List of constructor standings")
    metadata: StandingsMetadata = Field(description="Standings metadata")
    cache_info: Optional[CacheInfo] = Field(default=None, description="Cache information") 