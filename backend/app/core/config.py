# app/core/config.py
import os
from functools import lru_cache
from typing import List, Optional
from pydantic import validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    app_name: str = "NYC Transportation Optimizer"
    debug: bool = False
    environment: str = "development"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # API Keys
    google_maps_api_key: str
    uber_client_id: Optional[str] = None
    uber_client_secret: Optional[str] = None
    lyft_client_id: Optional[str] = None
    lyft_client_secret: Optional[str] = None
    
    # Database (for future use)
    database_url: Optional[str] = None
    
    # Redis (for caching)
    redis_url: Optional[str] = None
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_period: int = 60
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # NYC-specific pricing (in cents)
    nyc_subway_price: int = 290  # $2.90
    nyc_bus_price: int = 290     # $2.90
    
    #Add more complex pricing after MVP
    citi_bike_single_ride: int = 395  # $3.95 for 30 minutes
    
    @validator("google_maps_api_key")
    def validate_google_maps_api_key(cls, v):
        if not v or v == "your_google_maps_api_key_here":
            raise ValueError("GOOGLE_MAPS_API_KEY is required and must be set")
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of: {valid_levels}")
        return v.upper()
    
    @validator("environment")
    def validate_environment(cls, v):
        valid_envs = ["development", "staging", "production"]
        if v.lower() not in valid_envs:
            raise ValueError(f"ENVIRONMENT must be one of: {valid_envs}")
        return v.lower()

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    This ensures we only create one settings object and reuse it.
    """
    return Settings()


# Transportation service URLs and configurations
TRANSPORTATION_APIS = {
    "uber": {
        "base_url": "https://api.uber.com/v1.2",
        "auth_url": "https://login.uber.com/oauth/v2/token",
        "required_scopes": ["request"]
    },
    "lyft": {
        "base_url": "https://api.lyft.com/v1",
        "auth_url": "https://api.lyft.com/oauth/token",
        "required_scopes": ["public"]
    },
    "citi_bike": {
        "base_url": "https://gbfs.citibikenyc.com/gbfs/2.3",
        "station_info_url": "https://gbfs.citibikenyc.com/gbfs/2.3/en/station_information.json",
        "station_status_url": "https://gbfs.citibikenyc.com/gbfs/2.3/en/station_status.json"
    }
}

# NYC bounds for validation
NYC_BOUNDS = {
    "north": 40.917577,
    "south": 40.477399,
    "east": -73.700272,
    "west": -74.259090
}