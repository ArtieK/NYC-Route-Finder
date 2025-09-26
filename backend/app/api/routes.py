# app/api/routes.py
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from app.services.google_maps import GoogleMapsService
from app.services.transit_service import TransitService

router = APIRouter()

# Request/Response models
class RouteRequest(BaseModel):
    origin: str
    destination: str

class RouteResponse(BaseModel):
    origin: str
    destination: str
    routes: dict
    pricing: dict
    timestamp: str

@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify routing works"""
    return {"message": "API routes are working!"}

@router.post("/routes", response_model=RouteResponse)
async def get_routes(request: RouteRequest):
    """
    Get multi-modal transportation routes and pricing between two locations
    """
    try:
        maps_service = GoogleMapsService()
        result = await maps_service.get_multi_modal_routes(
            origin=request.origin,
            destination=request.destination
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting routes: {str(e)}")

@router.get("/routes")
async def get_routes_query(
    origin: str = Query(..., description="Starting location"),
    destination: str = Query(..., description="Destination location")
):
    """
    Get multi-modal transportation routes and pricing using query parameters
    """
    try:
        maps_service = GoogleMapsService()
        result = await maps_service.get_multi_modal_routes(
            origin=origin,
            destination=destination
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting routes: {str(e)}")

@router.get("/geocode")
async def geocode_address(address: str = Query(..., description="Address to geocode")):
    """
    Convert an address to coordinates
    """
    try:
        maps_service = GoogleMapsService()
        result = await maps_service.geocode_address(address)

        if not result:
            raise HTTPException(status_code=404, detail="Address not found")

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error geocoding address: {str(e)}")

@router.get("/transit")
async def get_transit_routes(
    origin: str = Query(..., description="Starting location"),
    destination: str = Query(..., description="Destination location"),
    departure_time: Optional[str] = Query("now", description="Departure time (default: now)")
):
    """
    Get detailed public transit routes for NYC (subway, bus, rail).
    Returns multiple route options with fares, transfers, and timing.
    """
    try:
        transit_service = TransitService()
        result = await transit_service.get_transit_directions(
            origin=origin,
            destination=destination,
            departure_time=departure_time
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting transit routes: {str(e)}")

@router.get("/transit/summary")
async def get_transit_summary(
    origin: str = Query(..., description="Starting location"),
    destination: str = Query(..., description="Destination location")
):
    """
    Get a simplified transit summary for quick comparison.
    Returns best route with essential information only.
    """
    try:
        transit_service = TransitService()
        result = await transit_service.get_transit_summary(
            origin=origin,
            destination=destination
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting transit summary: {str(e)}")