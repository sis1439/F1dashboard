from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os


class Settings(BaseSettings):
    """Application configuration settings"""
    
    # Application settings
    app_name: str = Field(default="F1 Dashboard API", env="APP_NAME")
    app_version: str = Field(default="2.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    
    # API settings
    api_prefix: str = Field(default="/api", env="API_PREFIX")
    allowed_origins: list = Field(default=["*"], env="ALLOWED_ORIGINS")
    
    # Cache settings
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    
    # Cache TTL settings (in seconds)
    cache_ttl_standings: int = Field(default=3600, env="CACHE_TTL_STANDINGS")  # 1 hour
    cache_ttl_schedule: int = Field(default=86400, env="CACHE_TTL_SCHEDULE")   # 1 day
    cache_ttl_race_results: int = Field(default=2592000, env="CACHE_TTL_RACE_RESULTS")  # 30 days
    
    # FastF1 settings
    fastf1_cache_dir: str = Field(default="./cache", env="FASTF1_CACHE_DIR")
    
    # Logging settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings() 