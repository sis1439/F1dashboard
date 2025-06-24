from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime


class BaseResponse(BaseModel):
    """Base response model for all API endpoints"""
    success: bool = Field(default=True, description="Indicates if the request was successful")
    message: Optional[str] = Field(default=None, description="Optional message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class ErrorResponse(BaseResponse):
    """Error response model"""
    success: bool = Field(default=False)
    error_code: Optional[str] = Field(default=None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")


class PaginatedResponse(BaseResponse):
    """Paginated response model"""
    total: int = Field(description="Total number of items")
    page: int = Field(default=1, description="Current page number")
    per_page: int = Field(default=10, description="Items per page")
    pages: int = Field(description="Total number of pages")


class CacheInfo(BaseModel):
    """Cache information model"""
    cached: bool = Field(description="Whether the data is from cache")
    cache_key: Optional[str] = Field(default=None, description="Cache key used")
    cached_at: Optional[datetime] = Field(default=None, description="When the data was cached")
    expires_at: Optional[datetime] = Field(default=None, description="When the cache expires") 