# app/services/google_maps.py
import os
import httpx
import asyncio
from dotenv import load_dotenv
from typing import Dict, List, Optional
from pprint import pprint

# Load environment variables
load_dotenv()

class GoogleMapsService:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_MAPS_API_KEY not found in environment variables")
        
        self.base_url = "https://maps.googleapis.com/maps/api"
    
    async def get_multi_modal_routes(self, origin: str, destination: str) -> Dict:
        """
        Get routes for all transportation modes and return structured data
        for our transportation optimizer
        """
        print(f"🗺️  Getting routes from {origin} to {destination}")
        
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
                        print(f"   ✅ {mode.capitalize()}: {route_info['duration']} ({route_info['distance']})")
                    else:
                        print(f"   ❌ {mode.capitalize()}: No route available")
                        
                except Exception as e:
                    print(f"   ❌ {mode.capitalize()}: Error - {str(e)}")
        
        # Structure the response for our transportation optimizer
        result = {
            "origin": origin,
            "destination": destination,
            "routes": routes_data,
            "pricing": {
                "rideshare": {
                    "uber": {"price": None, "duration": routes_data.get('driving', {}).get('duration_minutes'), "status": "pending"},
                    "lyft": {"price": None, "duration": routes_data.get('driving', {}).get('duration_minutes'), "status": "pending"}
                },
                "transit": {
                    "cta": {
                        "price": 250,  # $2.50 in cents for CTA
                        "duration": routes_data.get('transit', {}).get('duration_minutes'),
                        "status": "available" if 'transit' in routes_data else "unavailable"
                    }
                },
                "micromobility": {
                    "divvy": {
                        "price": None,  # Will be calculated based on duration
                        "duration": routes_data.get('bicycling', {}).get('duration_minutes'),
                        "status": "pending" if 'bicycling' in routes_data else "unavailable"
                    }
                }
            },
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
            print(f"Error getting {mode} directions: {str(e)}")
            return None
    
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


# Test function to verify the new structure
async def test_structured_response():
    """Test the new structured response format"""
    print("🚀 Testing Structured Google Maps Response\n")
    
    try:
        maps_service = GoogleMapsService()
        
        # Test Chicago locations
        origin = "Willis Tower, Chicago, IL"
        destination = "Navy Pier, Chicago, IL"
        
        result = await maps_service.get_multi_modal_routes(origin, destination)
        
        print("\n📊 Structured Response:")
        print("=" * 50)
        
        # Display routes summary
        print(f"🚩 Origin: {result['origin']}")
        print(f"🏁 Destination: {result['destination']}")
        print(f"⏰ Timestamp: {result['timestamp']}")
        
        print("\n🛣️  Available Routes:")
        for mode, route_info in result['routes'].items():
            print(f"   {mode.capitalize()}: {route_info['duration']} ({route_info['distance']})")
        
        print("\n💰 Pricing Structure:")
        for category, providers in result['pricing'].items():
            print(f"   {category.capitalize()}:")
            for provider, info in providers.items():
                price_str = f"${info['price']/100:.2f}" if info['price'] else "Pending"
                duration_str = f"{info['duration']}min" if info['duration'] else "N/A"
                print(f"      {provider.capitalize()}: {price_str} ({duration_str}) - {info['status']}")
        
        print("\n✅ Structure ready for price checking and mobile app!")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


if __name__ == "__main__":
    asyncio.run(test_structured_response())