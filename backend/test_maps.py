import os
import httpx
import asyncio
from dotenv import load_dotenv
from pprint import pprint

# Load environment variables
load_dotenv()

async def test_google_maps_api():
    """Simple test to verify Google Maps API is working"""
    
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        print("❌ Error: GOOGLE_MAPS_API_KEY not found in .env file")
        return
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Test locations in Chicago
    origin = "Willis Tower, Chicago, IL"  # Formerly Sears Tower
    destination = "Navy Pier, Chicago, IL"
    
    print(f"\n🚗 Testing route from {origin} to {destination}")
    
    # Test Directions API
    async with httpx.AsyncClient() as client:
        url = "https://maps.googleapis.com/maps/api/directions/json"
        
        # Test different modes
        modes = ['driving', 'transit', 'walking', 'bicycling']
        
        for mode in modes:
            print(f"\n📍 Testing {mode.upper()} mode:")
            
            params = {
                'origin': origin,
                'destination': destination,
                'mode': mode,
                'key': api_key
            }
            
            try:
                response = await client.get(url, params=params)
                data = response.json()
                
                if data['status'] == 'OK':
                    route = data['routes'][0]['legs'][0]
                    distance = route['distance']['text']
                    duration = route['duration']['text']
                    print(f"   ✅ Distance: {distance}")
                    print(f"   ✅ Duration: {duration}")
                else:
                    print(f"   ❌ Error: {data.get('status')} - {data.get('error_message', 'Unknown error')}")
                    
            except Exception as e:
                print(f"   ❌ Request failed: {str(e)}")
    
    # Test Geocoding API
    print("\n🗺️  Testing Geocoding API:")
    geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
    
    async with httpx.AsyncClient() as client:
        params = {
            'address': origin,
            'key': api_key
        }
        
        try:
            response = await client.get(geocode_url, params=params)
            data = response.json()
            
            if data['status'] == 'OK':
                location = data['results'][0]['geometry']['location']
                print(f"   ✅ Coordinates for {origin}:")
                print(f"      Latitude: {location['lat']}")
                print(f"      Longitude: {location['lng']}")
            else:
                print(f"   ❌ Geocoding error: {data.get('status')}")
                
        except Exception as e:
            print(f"   ❌ Geocoding failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 Google Maps API Test\n")
    asyncio.run(test_google_maps_api())