# app/services/google_maps.py
import os
import httpx
import asyncio
from dotenv import load_dotenv
from typing import Dict, List, Optional
from pprint import pprint
import logging

from .uber_service import UberService
from .lyft_service import LyftService

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class GoogleMapsService:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_MAPS_API_KEY not found in environment variables")
        
        self.base_url = "https://maps.googleapis.com/maps/api"
        
        # Initialize rideshare services for real-time pricing
        self.uber_service = UberService()
        self.lyft_service = LyftService()
    
    async def get_multi_modal_routes(self, origin: str, destination: str) -> Dict:
        """
        Get routes for all transportation modes and return structured data
        with real-time pricing from rideshare services
        """
        logger.info(f"🗺️  Getting routes from {origin} to {destination}")
        
        # Define modes we want to check
        modes = ['driving', 'transit', 'walking', 'bicycling']
        routes_data = {}
        
        async with httpx.AsyncClient() as client:
            # Get routes for each mode
            for mode in modes:
                try:
                    route_info = await self._get_directions(client, origin, destination, mode)
                    if route_info:
                        routes_data[mode] = route_info
                        logger.info(f"   ✅ {mode.capitalize()}: {route_info['duration']} ({route_info['distance']})")
                    else:
                        logger.info(f"   ❌ {mode.capitalize()}: No route available")
                        
                except Exception as e:
                    logger.error(f"   ❌ {mode.capitalize()}: Error - {str(e)}")
        
        # Get coordinates for pricing APIs
        origin_coords = await self.geocode_address(origin)
        destination_coords = await self.geocode_address(destination)
        
        # Get real-time rideshare pricing
        pricing_data = await self._get_rideshare_pricing(
            origin_coords, destination_coords, routes_data
        )
        
        # Structure the response for our transportation optimizer
        result = {
            "origin": origin,
            "destination": destination,
            "routes": routes_data,
            "pricing": pricing_data,
            "timestamp": self._get_timestamp()
        }
        
        return result
    
    async def _get_directions(self, client: httpx.AsyncClient, origin: str, destination: str, mode: str) -> Optional[Dict]:
        """Get directions for a specific transportation mode"""
        url = f"{self.base_url}/directions/json"
        
        params = {
            'origin': origin,
            'destination': destination,
            'mode': mode,
            'alternatives': True,  # Get multiple route options
            'key': self.api_key
        }
        
        try:
            response = await client.get(url, params=params)
            data = response.json()
            
            if data['status'] != 'OK':
                return None
            
            # Extract the main route (first option)
            route = data['routes'][0]['legs'][0]
            
            return {
                "distance": route['distance']['text'],
                "distance_meters": route['distance']['value'],
                "duration": route['duration']['text'], 
                "duration_minutes": round(route['duration']['value'] / 60),
                "start_address": route['start_address'],
                "end_address": route['end_address'],
                "steps": len(route['steps']),
                "mode": mode,
                "raw_data": data  # Keep original data for detailed analysis
            }
            
        except Exception as e:
            logger.error(f"Error getting {mode} directions: {str(e)}")
            return None
    
    async def _get_rideshare_pricing(self, origin_coords: Optional[Dict], 
                                   destination_coords: Optional[Dict], 
                                   routes_data: Dict) -> Dict:
        """
        Get real-time pricing from rideshare services (Uber & Lyft)
        """
        pricing_data = {
            "rideshare": {
                "uber": {"price": None, "duration": None, "status": "unavailable"},
                "lyft": {"price": None, "duration": None, "status": "unavailable"}
            },
            "transit": {
                "mta": {
                    "price": 290,  # $2.90 for NYC MTA
                    "duration": routes_data.get('transit', {}).get('duration_minutes'),
                    "status": "available" if 'transit' in routes_data else "unavailable"
                }
            },
            "micromobility": {
                "citi_bike": {
                    "price": None,  # Will be calculated based on duration
                    "duration": routes_data.get('bicycling', {}).get('duration_minutes'),
                    "status": "pending" if 'bicycling' in routes_data else "unavailable"
                }
            }
        }
        
        # Only get rideshare pricing if we have valid coordinates
        if not origin_coords or not destination_coords:
            logger.warning("Cannot get rideshare pricing without valid coordinates")
            return pricing_data
        
        try:
            # Get driving duration for rideshare estimates
            driving_duration = routes_data.get('driving', {}).get('duration_minutes')
            
            # Call Uber and Lyft APIs concurrently for better performance
            uber_task = self._get_uber_pricing(
                origin_coords, destination_coords, driving_duration
            )
            lyft_task = self._get_lyft_pricing(
                origin_coords, destination_coords, driving_duration
            )
            
            uber_pricing, lyft_pricing = await asyncio.gather(
                uber_task, lyft_task, return_exceptions=True
            )
            
            # Process Uber results
            if isinstance(uber_pricing, dict) and not isinstance(uber_pricing, Exception):
                pricing_data["rideshare"]["uber"] = uber_pricing
                logger.info(f"   ✅ Uber pricing retrieved successfully")
            else:
                logger.warning(f"   ⚠️ Uber pricing failed: {uber_pricing}")
            
            # Process Lyft results
            if isinstance(lyft_pricing, dict) and not isinstance(lyft_pricing, Exception):
                pricing_data["rideshare"]["lyft"] = lyft_pricing
                logger.info(f"   ✅ Lyft pricing retrieved successfully")
            else:
                logger.warning(f"   ⚠️ Lyft pricing failed: {lyft_pricing}")
                
        except Exception as e:
            logger.error(f"Error getting rideshare pricing: {str(e)}")
        
        return pricing_data
    
    async def _get_uber_pricing(self, origin_coords: Dict, destination_coords: Dict, 
                              driving_duration: Optional[int]) -> Dict:
        """Get Uber pricing estimates"""
        try:
            estimates = await self.uber_service.get_price_estimates(
                origin_coords['lat'], origin_coords['lng'],
                destination_coords['lat'], destination_coords['lng']
            )
            
            # Extract the best/cheapest option (typically UberX)
            products = estimates.get('products', {})
            if 'uberx' in products:
                product = products['uberx']
                return {
                    "price": product.get('low_estimate'),  # in cents
                    "price_range": f"${product.get('low_estimate', 0)/100:.0f}-${product.get('high_estimate', 0)/100:.0f}",
                    "duration": driving_duration,
                    "status": product.get('status', 'available'),
                    "service": "uber",
                    "product_type": "uberx"
                }
            elif products:
                # Fallback to first available product
                first_product = next(iter(products.values()))
                return {
                    "price": first_product.get('low_estimate'),
                    "price_range": first_product.get('estimate', 'N/A'),
                    "duration": driving_duration,
                    "status": first_product.get('status', 'available'),
                    "service": "uber",
                    "product_type": next(iter(products.keys()))
                }
            else:
                return {"price": None, "duration": driving_duration, "status": "unavailable"}
                
        except Exception as e:
            logger.error(f"Error getting Uber pricing: {str(e)}")
            return {"price": None, "duration": driving_duration, "status": "error"}
    
    async def _get_lyft_pricing(self, origin_coords: Dict, destination_coords: Dict,
                              driving_duration: Optional[int]) -> Dict:
        """Get Lyft pricing estimates"""  
        try:
            estimates = await self.lyft_service.get_cost_estimates(
                origin_coords['lat'], origin_coords['lng'],
                destination_coords['lat'], destination_coords['lng']
            )
            
            # Extract the standard Lyft option
            products = estimates.get('products', {})
            if 'lyft_standard' in products:
                product = products['lyft_standard']
                return {
                    "price": product.get('estimated_cost_cents_min'),  # in cents
                    "price_range": f"${product.get('estimated_cost_cents_min', 0)/100:.0f}-${product.get('estimated_cost_cents_max', 0)/100:.0f}",
                    "duration": driving_duration,
                    "status": product.get('status', 'available'),
                    "service": "lyft", 
                    "product_type": "lyft_standard"
                }
            elif products:
                # Fallback to first available product
                first_product = next(iter(products.values()))
                return {
                    "price": first_product.get('estimated_cost_cents_min'),
                    "price_range": f"${first_product.get('estimated_cost_cents_min', 0)/100:.0f}-${first_product.get('estimated_cost_cents_max', 0)/100:.0f}",
                    "duration": driving_duration,
                    "status": first_product.get('status', 'available'),
                    "service": "lyft",
                    "product_type": next(iter(products.keys()))
                }
            else:
                return {"price": None, "duration": driving_duration, "status": "unavailable"}
                
        except Exception as e:
            logger.error(f"Error getting Lyft pricing: {str(e)}")
            return {"price": None, "duration": driving_duration, "status": "error"}
    
    async def geocode_address(self, address: str) -> Optional[Dict]:
        """Convert address to coordinates"""
        url = f"{self.base_url}/geocode/json"
        
        params = {
            'address': address,
            'key': self.api_key
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params)
                data = response.json()
                
                if data['status'] == 'OK':
                    result = data['results'][0]
                    location = result['geometry']['location']
                    
                    return {
                        "address": result['formatted_address'],
                        "lat": location['lat'],
                        "lng": location['lng'],
                        "place_id": result.get('place_id'),
                        "types": result.get('types', [])
                    }
                    
            except Exception as e:
                print(f"Geocoding error: {str(e)}")
                
        return None
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()


# Test function to verify the new integrated pricing
async def test_integrated_pricing():
    """Test the new integrated pricing system"""
    print("🚀 Testing Integrated Pricing System\n")
    
    try:
        maps_service = GoogleMapsService()
        
        # Test NYC locations for realistic rideshare availability
        origin = "Times Square, New York, NY"
        destination = "Central Park, New York, NY"
        
        result = await maps_service.get_multi_modal_routes(origin, destination)
        
        print("\n📊 Integrated Response:")
        print("=" * 50)
        
        # Display routes summary
        print(f"🚩 Origin: {result['origin']}")
        print(f"🏁 Destination: {result['destination']}")
        print(f"⏰ Timestamp: {result['timestamp']}")
        
        print("\n🛣️  Available Routes:")
        for mode, route_info in result['routes'].items():
            print(f"   {mode.capitalize()}: {route_info['duration']} ({route_info['distance']})")
        
        print("\n💰 Real-time Pricing:")
        for category, providers in result['pricing'].items():
            print(f"   {category.capitalize()}:")
            for provider, info in providers.items():
                if info.get('price'):
                    price_str = f"${info['price']/100:.2f}"
                    if info.get('price_range'):
                        price_str = info['price_range']
                elif info.get('price') == 0:
                    price_str = "Free"
                else:
                    price_str = "N/A"
                    
                duration_str = f"{info['duration']}min" if info['duration'] else "N/A"
                service_str = f"({info.get('service', provider)})" if info.get('service') else ""
                print(f"      {provider.capitalize()}: {price_str} - {duration_str} - {info['status']} {service_str}")
        
        print("\n✅ Integrated pricing system working!")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


if __name__ == "__main__":
    asyncio.run(test_integrated_pricing())