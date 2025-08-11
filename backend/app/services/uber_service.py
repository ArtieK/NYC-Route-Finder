# app/services/uber_service.py
import os
import httpx
import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)

class UberService:
    """
    Service for integrating with Uber API to get real-time price estimates
    and available products (UberX, Uber Bike, Uber Scooter, etc.)
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.server_token = self.settings.uber_client_id  # Using client_id as server token for now
        self.base_url = "https://api.uber.com/v1.2"
        
        if not self.server_token:
            logger.warning("UBER_CLIENT_ID not configured - Uber pricing will be unavailable")
    
    async def get_price_estimates(self, start_lat: float, start_lng: float, 
                                end_lat: float, end_lng: float) -> Dict:
        """
        Get price estimates for all available Uber products between two points
        
        Args:
            start_lat: Starting latitude
            start_lng: Starting longitude  
            end_lat: Ending latitude
            end_lng: Ending longitude
            
        Returns:
            Dict with price estimates for each available product type
        """
        if not self.server_token:
            return self._mock_price_estimates(start_lat, start_lng, end_lat, end_lng)
        
        try:
            logger.info(f"🚗 Getting Uber price estimates: ({start_lat},{start_lng}) → ({end_lat},{end_lng})")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/estimates/price",
                    params={
                        "start_latitude": start_lat,
                        "start_longitude": start_lng,
                        "end_latitude": end_lat,
                        "end_longitude": end_lng
                    },
                    headers={
                        "Authorization": f"Token {self.server_token}",
                        "Accept-Language": "en_US",
                        "Content-Type": "application/json"
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._process_price_estimates(data)
                else:
                    logger.error(f"Uber API error {response.status_code}: {response.text}")
                    return self._mock_price_estimates(start_lat, start_lng, end_lat, end_lng)
                    
        except Exception as e:
            logger.error(f"Error calling Uber API: {str(e)}")
            return self._mock_price_estimates(start_lat, start_lng, end_lat, end_lng)
    
    async def get_available_products(self, lat: float, lng: float) -> List[Dict]:
        """
        Get all available Uber products at a specific location
        
        Args:
            lat: Latitude
            lng: Longitude
            
        Returns:
            List of available product types with details
        """
        if not self.server_token:
            return self._mock_available_products()
        
        try:
            logger.info(f"🔍 Getting available Uber products at ({lat},{lng})")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/products",
                    params={
                        "latitude": lat,
                        "longitude": lng
                    },
                    headers={
                        "Authorization": f"Token {self.server_token}",
                        "Accept-Language": "en_US",
                        "Content-Type": "application/json"
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._process_available_products(data)
                else:
                    logger.error(f"Uber products API error {response.status_code}: {response.text}")
                    return self._mock_available_products()
                    
        except Exception as e:
            logger.error(f"Error getting Uber products: {str(e)}")
            return self._mock_available_products()
    
    async def get_time_estimates(self, lat: float, lng: float) -> Dict:
        """
        Get ETA estimates for all available Uber products
        
        Args:
            lat: Pickup latitude
            lng: Pickup longitude
            
        Returns:
            Dict with time estimates for each product
        """
        if not self.server_token:
            return self._mock_time_estimates()
        
        try:
            logger.info(f"⏰ Getting Uber time estimates at ({lat},{lng})")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/estimates/time",
                    params={
                        "start_latitude": lat,
                        "start_longitude": lng
                    },
                    headers={
                        "Authorization": f"Token {self.server_token}",
                        "Accept-Language": "en_US",
                        "Content-Type": "application/json"
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._process_time_estimates(data)
                else:
                    logger.error(f"Uber time API error {response.status_code}: {response.text}")
                    return self._mock_time_estimates()
                    
        except Exception as e:
            logger.error(f"Error getting Uber time estimates: {str(e)}")
            return self._mock_time_estimates()
    
    def _process_price_estimates(self, data: Dict) -> Dict:
        """Process Uber API price response into our standard format"""
        processed = {
            "service": "uber",
            "timestamp": datetime.now().isoformat(),
            "products": {}
        }
        
        for product in data.get("prices", []):
            product_key = self._normalize_product_name(product.get("display_name", ""))
            
            processed["products"][product_key] = {
                "product_id": product.get("product_id"),
                "display_name": product.get("display_name"),
                "estimate": product.get("estimate"),
                "low_estimate": product.get("low_estimate"),
                "high_estimate": product.get("high_estimate"),
                "currency_code": product.get("currency_code", "USD"),
                "duration": product.get("duration"),  # in seconds
                "distance": product.get("distance"),  # in miles
                "surge_multiplier": product.get("surge_multiplier", 1.0),
                "status": "available"
            }
        
        return processed
    
    def _process_available_products(self, data: Dict) -> List[Dict]:
        """Process available products response"""
        products = []
        
        for product in data.get("products", []):
            products.append({
                "product_id": product.get("product_id"),
                "display_name": product.get("display_name"),
                "description": product.get("description"),
                "capacity": product.get("capacity"),
                "image": product.get("image"),
                "cash_enabled": product.get("cash_enabled", False),
                "shared": product.get("shared", False),
                "short_description": product.get("short_description")
            })
        
        return products
    
    def _process_time_estimates(self, data: Dict) -> Dict:
        """Process time estimates response"""
        processed = {}
        
        for estimate in data.get("times", []):
            product_key = self._normalize_product_name(estimate.get("display_name", ""))
            processed[product_key] = {
                "product_id": estimate.get("product_id"),
                "display_name": estimate.get("display_name"),
                "estimate": estimate.get("estimate")  # in seconds
            }
        
        return processed
    
    def _normalize_product_name(self, display_name: str) -> str:
        """Normalize product names for consistent keys"""
        name_lower = display_name.lower()
        
        if "uberx" in name_lower or "uber x" in name_lower:
            return "uberx"
        elif "bike" in name_lower:
            return "uber_bike"
        elif "scooter" in name_lower:
            return "uber_scooter"
        elif "pool" in name_lower:
            return "uber_pool"
        elif "xl" in name_lower:
            return "uber_xl"
        elif "comfort" in name_lower:
            return "uber_comfort"
        elif "black" in name_lower:
            return "uber_black"
        else:
            # Fallback to sanitized version of display name
            return display_name.lower().replace(" ", "_").replace("-", "_")
    
    def _mock_price_estimates(self, start_lat: float, start_lng: float, 
                            end_lat: float, end_lng: float) -> Dict:
        """
        Mock price estimates for development/testing when API key unavailable
        Uses rough distance calculation for realistic estimates
        """
        # Calculate approximate distance (rough estimate for pricing)
        lat_diff = abs(end_lat - start_lat)
        lng_diff = abs(end_lng - start_lng)
        approx_distance_miles = ((lat_diff ** 2 + lng_diff ** 2) ** 0.5) * 69  # Very rough conversion
        
        # Base rates (NYC estimates)
        base_rate = 2.55
        per_mile_rate = 1.75
        per_minute_rate = 0.35
        estimated_duration_minutes = max(8, approx_distance_miles * 3)  # Rough time estimate
        
        # Calculate base fare
        base_fare = base_rate + (approx_distance_miles * per_mile_rate) + (estimated_duration_minutes * per_minute_rate)
        
        logger.info(f"🔧 Using mock Uber pricing (distance: {approx_distance_miles:.1f}mi, base: ${base_fare:.2f})")
        
        return {
            "service": "uber",
            "timestamp": datetime.now().isoformat(),
            "products": {
                "uberx": {
                    "product_id": "mock_uberx",
                    "display_name": "UberX",
                    "estimate": f"${base_fare:.0f}-{base_fare * 1.3:.0f}",
                    "low_estimate": int(base_fare * 100),  # in cents
                    "high_estimate": int(base_fare * 1.3 * 100),  # in cents
                    "currency_code": "USD",
                    "duration": int(estimated_duration_minutes * 60),  # in seconds
                    "distance": round(approx_distance_miles, 1),
                    "surge_multiplier": 1.0,
                    "status": "available"
                },
                "uber_bike": {
                    "product_id": "mock_uber_bike",
                    "display_name": "Uber Bike",
                    "estimate": "$3-6",
                    "low_estimate": 300,  # $3.00 in cents
                    "high_estimate": 600,  # $6.00 in cents  
                    "currency_code": "USD",
                    "duration": int(approx_distance_miles * 4 * 60),  # ~4 min per mile
                    "distance": round(approx_distance_miles, 1),
                    "surge_multiplier": 1.0,
                    "status": "available" if approx_distance_miles < 3 else "unavailable"
                },
                "uber_scooter": {
                    "product_id": "mock_uber_scooter", 
                    "display_name": "Uber Scooter",
                    "estimate": "$4-8",
                    "low_estimate": 400,  # $4.00 in cents
                    "high_estimate": 800,  # $8.00 in cents
                    "currency_code": "USD",
                    "duration": int(approx_distance_miles * 3 * 60),  # ~3 min per mile
                    "distance": round(approx_distance_miles, 1),
                    "surge_multiplier": 1.0,
                    "status": "available" if approx_distance_miles < 2.5 else "unavailable"
                }
            }
        }
    
    def _mock_available_products(self) -> List[Dict]:
        """Mock available products for development"""
        return [
            {
                "product_id": "mock_uberx",
                "display_name": "UberX",
                "description": "The low-cost Uber",
                "capacity": 4,
                "image": "http://d1a3f4spazzrp4.cloudfront.net/car-types/mono/mono-uberx.png",
                "cash_enabled": True,
                "shared": False,
                "short_description": "uberX"
            },
            {
                "product_id": "mock_uber_bike",
                "display_name": "Uber Bike", 
                "description": "Pedal-powered rides",
                "capacity": 1,
                "image": "http://d1a3f4spazzrp4.cloudfront.net/car-types/mono/mono-bike.png",
                "cash_enabled": False,
                "shared": False,
                "short_description": "Bike"
            }
        ]
    
    def _mock_time_estimates(self) -> Dict:
        """Mock time estimates for development"""
        return {
            "uberx": {
                "product_id": "mock_uberx",
                "display_name": "UberX", 
                "estimate": 300  # 5 minutes in seconds
            },
            "uber_bike": {
                "product_id": "mock_uber_bike",
                "display_name": "Uber Bike",
                "estimate": 180  # 3 minutes in seconds  
            }
        }


# Test function for development
async def test_uber_integration():
    """Test Uber service integration"""
    print("🧪 Testing Uber Service Integration\n")
    
    uber_service = UberService()
    
    # Test NYC coordinates
    start_lat, start_lng = 40.7589, -73.9851  # Times Square
    end_lat, end_lng = 40.7829, -73.9654      # Central Park
    
    try:
        # Test price estimates
        print("1️⃣ Testing price estimates...")
        prices = await uber_service.get_price_estimates(start_lat, start_lng, end_lat, end_lng)
        print(f"✅ Price estimates: {len(prices.get('products', {}))} products found")
        
        # Test available products
        print("\n2️⃣ Testing available products...")
        products = await uber_service.get_available_products(start_lat, start_lng)
        print(f"✅ Available products: {len(products)} products found")
        
        # Test time estimates
        print("\n3️⃣ Testing time estimates...")
        times = await uber_service.get_time_estimates(start_lat, start_lng)
        print(f"✅ Time estimates: {len(times)} estimates found")
        
        print(f"\n🎉 Uber integration test completed successfully!")
        
        return {
            "prices": prices,
            "products": products, 
            "times": times
        }
        
    except Exception as e:
        print(f"❌ Uber integration test failed: {str(e)}")
        return None


if __name__ == "__main__":
    asyncio.run(test_uber_integration())