"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class RouteRequest(BaseModel):
    """Request schema for route comparison."""
    origin: str = Field(..., min_length=3, max_length=200)
    destination: str = Field(..., min_length=3, max_length=200)

    class Config:
        json_schema_extra = {
            "example": {
                "origin": "Times Square, New York, NY",
                "destination": "Brooklyn Bridge, New York, NY"
            }
        }


class TransportOption(BaseModel):
    """Schema for a single transportation option."""
    provider: str
    vehicle_type: str
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    duration: Optional[int] = None  # in minutes
    distance: Optional[float] = None  # in miles
    available: bool = True
    details: Optional[Dict[str, Any]] = None


class RouteResponse(BaseModel):
    """Response schema for route comparison."""
    origin: str
    destination: str
    distance: Optional[str] = None
    duration: Optional[str] = None
    options: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "origin": "Times Square, New York, NY",
                "destination": "Brooklyn Bridge, New York, NY",
                "distance": "5.2 miles",
                "duration": "18 minutes",
                "options": {
                    "uber": {
                        "uberx": {"price": "$15-20", "duration": "18 min"}
                    }
                }
            }
        }


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str
    status_code: int
    details: Optional[str] = None
