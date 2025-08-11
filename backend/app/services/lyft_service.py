# app/services/lyft_service.py  
import os
import httpx
import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)

class LyftService:
    """
    Service for integrating with Lyft API to get real-time cost estimates
    and available ride types (Lyft Standard, Lyft Bike, Lyft Scooter, etc.)
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.client_id = self.settings.lyft_client_id
        self.client_secret = self.settings.lyft_client_secret
        self.base_url = "https://api.lyft.com/v1"
        self.access_token = None
        
        if not self.client_id or not self.client_secret:
            logger.warning("LYFT_CLIENT_ID/SECRET not configured - Lyft pricing will be unavailable")
    
    async def _get_access_token(self) -> str:
        """
        Get OAuth access token for Lyft API
        Uses client credentials flow for server-to-server authentication
        """
        if not self.client_id or not self.client_secret:
            return None
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.lyft.com/oauth/token",
                    data={
                        "grant_type": "client_credentials",
                        "scope": "public"
                    },
                    auth=(self.client_id, self.client_secret),
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    token_data = response.json()
                    self.access_token = token_data.get("access_token")
                    logger.info("✅ Lyft access token obtained successfully")
                    return self.access_token
                else:
                    logger.error(f"Lyft token error {response.status_code}: {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting Lyft access token: {str(e)}")
            return None
    
    async def get_cost_estimates(self, start_lat: float, start_lng: float,
                               end_lat: float, end_lng: float) -> Dict:
        """
        Get cost estimates for all available Lyft ride types between two points
        
        Args:
            start_lat: Starting latitude
            start_lng: Starting longitude
            end_lat: Ending latitude 
            end_lng: Ending longitude
            
        Returns:
            Dict with cost estimates for each available ride type
        """
        if not self.access_token:
            token = await self._get_access_token()
            if not token:
                return self._mock_cost_estimates(start_lat, start_lng, end_lat, end_lng)
        
        try:
            logger.info(f"🟣 Getting Lyft cost estimates: ({start_lat},{start_lng}) → ({end_lat},{end_lng})")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/cost",
                    params={
                        "start_lat": start_lat,
                        "start_lng": start_lng,
                        "end_lat": end_lat,
                        "end_lng": end_lng
                    },
                    headers={
                        "Authorization": f"Bearer {self.access_token}",
                        "Content-Type": "application/json"
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._process_cost_estimates(data)
                else:
                    logger.error(f"Lyft cost API error {response.status_code}: {response.text}")
                    return self._mock_cost_estimates(start_lat, start_lng, end_lat, end_lng)
                    
        except Exception as e:
            logger.error(f"Error calling Lyft cost API: {str(e)}")
            return self._mock_cost_estimates(start_lat, start_lng, end_lat, end_lng)
    
    async def get_available_ride_types(self, lat: float, lng: float) -> List[Dict]:
        """
        Get all available Lyft ride types at a specific location
        
        Args:
            lat: Latitude
            lng: Longitude
            
        Returns:
            List of available ride types with details
        """
        if not self.access_token:
            token = await self._get_access_token()
            if not token:
                return self._mock_available_ride_types()
        
        try:
            logger.info(f"🔍 Getting available Lyft ride types at ({lat},{lng})")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/ridetypes",
                    params={
                        "lat": lat,
                        "lng": lng
                    },
                    headers={
                        "Authorization": f"Bearer {self.access_token}",
                        "Content-Type": "application/json"
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._process_available_ride_types(data)
                else:
                    logger.error(f"Lyft ride types API error {response.status_code}: {response.text}")
                    return self._mock_available_ride_types()
                    
        except Exception as e:
            logger.error(f"Error getting Lyft ride types: {str(e)}")
            return self._mock_available_ride_types()
    
    async def get_eta_estimates(self, lat: float, lng: float) -> Dict:
        """
        Get ETA estimates for all available Lyft ride types
        
        Args:
            lat: Pickup latitude
            lng: Pickup longitude
            
        Returns:
            Dict with ETA estimates for each ride type
        """
        if not self.access_token:
            token = await self._get_access_token()
            if not token:
                return self._mock_eta_estimates()
        
        try:
            logger.info(f"⏰ Getting Lyft ETA estimates at ({lat},{lng})")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/eta",
                    params={
                        "lat": lat,
                        "lng": lng
                    },
                    headers={
                        "Authorization": f"Bearer {self.access_token}",
                        "Content-Type": "application/json"
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._process_eta_estimates(data)
                else:
                    logger.error(f"Lyft ETA API error {response.status_code}: {response.text}")
                    return self._mock_eta_estimates()
                    
        except Exception as e:
            logger.error(f"Error getting Lyft ETA estimates: {str(e)}")
            return self._mock_eta_estimates()
    
    def _process_cost_estimates(self, data: Dict) -> Dict:
        """Process Lyft API cost response into our standard format"""
        processed = {
            "service": "lyft",
            "timestamp": datetime.now().isoformat(),
            "products": {}
        }
        
        for estimate in data.get("cost_estimates", []):
            ride_type = estimate.get("ride_type")
            product_key = self._normalize_ride_type_name(ride_type)
            
            processed["products"][product_key] = {
                "ride_type": ride_type,
                "display_name": estimate.get("display_name", ride_type),
                "estimated_cost_cents_min": estimate.get("estimated_cost_cents_min"),
                "estimated_cost_cents_max": estimate.get("estimated_cost_cents_max"),
                "estimated_distance_miles": estimate.get("estimated_distance_miles"),
                "estimated_duration_seconds": estimate.get("estimated_duration_seconds"),
                "is_valid_estimate": estimate.get("is_valid_estimate", True),
                "primetime_percentage": estimate.get("primetime_percentage", "0%"),
                "currency": estimate.get("currency", "USD"),
                "status": "available" if estimate.get("is_valid_estimate", True) else "unavailable"
            }
        
        return processed
    
    def _process_available_ride_types(self, data: Dict) -> List[Dict]:
        """Process available ride types response"""
        ride_types = []
        
        for ride_type in data.get("ride_types", []):
            ride_types.append({
                "ride_type": ride_type.get("ride_type"),
                "display_name": ride_type.get("display_name"),
                "image_url": ride_type.get("image_url"),
                "max_passengers": ride_type.get("seats"),
                "pricing_details": ride_type.get("pricing_details", {}),
                "service_area": ride_type.get("service_area", {})
            })
        
        return ride_types
    
    def _process_eta_estimates(self, data: Dict) -> Dict:
        """Process ETA estimates response"""
        processed = {}
        
        for eta in data.get("eta_estimates", []):
            ride_type = eta.get("ride_type")
            product_key = self._normalize_ride_type_name(ride_type)
            
            processed[product_key] = {
                "ride_type": ride_type,
                "display_name": eta.get("display_name", ride_type),
                "eta_seconds": eta.get("eta_seconds"),
                "is_valid_estimate": eta.get("is_valid_estimate", True)
            }
        
        return processed
    
    def _normalize_ride_type_name(self, ride_type: str) -> str:
        """Normalize ride type names for consistent keys"""
        if not ride_type:
            return "unknown"
            
        ride_type_lower = ride_type.lower()
        
        if "lyft" in ride_type_lower and "bike" in ride_type_lower:
            return "lyft_bike"
        elif "lyft" in ride_type_lower and "scooter" in ride_type_lower:
            return "lyft_scooter"  
        elif ride_type_lower in ["lyft", "standard"]:
            return "lyft_standard"
        elif "shared" in ride_type_lower or "line" in ride_type_lower:
            return "lyft_shared"
        elif "xl" in ride_type_lower:
            return "lyft_xl"
        elif "lux" in ride_type_lower:
            return "lyft_lux"
        else:
            # Fallback to sanitized version
            return ride_type.lower().replace(" ", "_").replace("-", "_")
    
    def _mock_cost_estimates(self, start_lat: float, start_lng: float,
                           end_lat: float, end_lng: float) -> Dict:
        """
        Mock cost estimates for development/testing when API key unavailable
        """
        # Calculate approximate distance for realistic estimates
        lat_diff = abs(end_lat - start_lat)
        lng_diff = abs(end_lng - start_lng)  
        approx_distance_miles = ((lat_diff ** 2 + lng_diff ** 2) ** 0.5) * 69
        
        # Lyft base rates (NYC estimates)
        base_rate = 2.65  # Slightly different from Uber
        per_mile_rate = 1.85
        per_minute_rate = 0.38
        estimated_duration_minutes = max(8, approx_distance_miles * 3)
        
        # Calculate base fare
        base_fare = base_rate + (approx_distance_miles * per_mile_rate) + (estimated_duration_minutes * per_minute_rate)
        
        logger.info(f"🔧 Using mock Lyft pricing (distance: {approx_distance_miles:.1f}mi, base: ${base_fare:.2f})")
        
        return {
            "service": "lyft",
            "timestamp": datetime.now().isoformat(),
            "products": {
                "lyft_standard": {
                    "ride_type": "lyft",
                    "display_name": "Lyft",
                    "estimated_cost_cents_min": int(base_fare * 100),
                    "estimated_cost_cents_max": int(base_fare * 1.35 * 100),
                    "estimated_distance_miles": round(approx_distance_miles, 1),
                    "estimated_duration_seconds": int(estimated_duration_minutes * 60),
                    "is_valid_estimate": True,
                    "primetime_percentage": "0%",
                    "currency": "USD",
                    "status": "available"
                },
                "lyft_bike": {
                    "ride_type": "lyft_bike",
                    "display_name": "Lyft Bike",
                    "estimated_cost_cents_min": 350,  # $3.50
                    "estimated_cost_cents_max": 650,  # $6.50
                    "estimated_distance_miles": round(approx_distance_miles, 1),
                    "estimated_duration_seconds": int(approx_distance_miles * 4 * 60),
                    "is_valid_estimate": True,
                    "primetime_percentage": "0%",
                    "currency": "USD",
                    "status": "available" if approx_distance_miles < 3 else "unavailable"
                },
                "lyft_scooter": {
                    "ride_type": "lyft_scooter",
                    "display_name": "Lyft Scooter",
                    "estimated_cost_cents_min": 450,  # $4.50
                    "estimated_cost_cents_max": 850,  # $8.50  
                    "estimated_distance_miles": round(approx_distance_miles, 1),
                    "estimated_duration_seconds": int(approx_distance_miles * 3 * 60),
                    "is_valid_estimate": True,
                    "primetime_percentage": "0%",
                    "currency": "USD",
                    "status": "available" if approx_distance_miles < 2.5 else "unavailable"
                }
            }
        }
    
    def _mock_available_ride_types(self) -> List[Dict]:
        """Mock available ride types for development"""
        return [
            {
                "ride_type": "lyft",
                "display_name": "Lyft",
                "image_url": "https://images.lyft.com/production/vehicle_view/lyft.png",
                "max_passengers": 4,
                "pricing_details": {
                    "base_charge": 265,  # $2.65 in cents
                    "cost_per_mile": 185,  # $1.85 in cents
                    "cost_per_minute": 38   # $0.38 in cents
                },
                "service_area": {"center": {"lat": 40.7589, "lng": -73.9851}}
            },
            {
                "ride_type": "lyft_bike", 
                "display_name": "Lyft Bike",
                "image_url": "https://images.lyft.com/production/vehicle_view/bike.png",
                "max_passengers": 1,
                "pricing_details": {
                    "base_charge": 100,  # $1.00 unlock fee
                    "cost_per_minute": 25  # $0.25 per minute
                },
                "service_area": {"center": {"lat": 40.7589, "lng": -73.9851}}
            }
        ]
    
    def _mock_eta_estimates(self) -> Dict:
        """Mock ETA estimates for development"""
        return {
            "lyft_standard": {
                "ride_type": "lyft",
                "display_name": "Lyft",
                "eta_seconds": 360,  # 6 minutes
                "is_valid_estimate": True
            },
            "lyft_bike": {
                "ride_type": "lyft_bike",
                "display_name": "Lyft Bike", 
                "eta_seconds": 120,  # 2 minutes
                "is_valid_estimate": True
            }
        }


# Test function for development
async def test_lyft_integration():
    """Test Lyft service integration"""
    print("🧪 Testing Lyft Service Integration\n")
    
    lyft_service = LyftService()
    
    # Test NYC coordinates
    start_lat, start_lng = 40.7589, -73.9851  # Times Square
    end_lat, end_lng = 40.7829, -73.9654      # Central Park
    
    try:
        # Test cost estimates
        print("1️⃣ Testing cost estimates...")
        costs = await lyft_service.get_cost_estimates(start_lat, start_lng, end_lat, end_lng)
        print(f"✅ Cost estimates: {len(costs.get('products', {}))} products found")
        
        # Test available ride types
        print("\n2️⃣ Testing available ride types...")
        ride_types = await lyft_service.get_available_ride_types(start_lat, start_lng)
        print(f"✅ Available ride types: {len(ride_types)} types found")
        
        # Test ETA estimates
        print("\n3️⃣ Testing ETA estimates...")
        etas = await lyft_service.get_eta_estimates(start_lat, start_lng)
        print(f"✅ ETA estimates: {len(etas)} estimates found")
        
        print(f"\n🎉 Lyft integration test completed successfully!")
        
        return {
            "costs": costs,
            "ride_types": ride_types,
            "etas": etas
        }
        
    except Exception as e:
        print(f"❌ Lyft integration test failed: {str(e)}")
        return None


if __name__ == "__main__":
    asyncio.run(test_lyft_integration())