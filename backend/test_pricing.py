#!/usr/bin/env python3
"""
Simple test script for the integrated pricing system
This avoids config dependencies and tests with mock data
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

load_dotenv()

# Set a mock Google Maps API key for testing if not present
if not os.getenv('GOOGLE_MAPS_API_KEY'):
    os.environ['GOOGLE_MAPS_API_KEY'] = 'test_key_for_demo'

async def test_pricing_integration():
    """Test the integrated pricing system with mock data"""
    print("🧪 Testing Integrated Pricing System")
    print("=" * 50)
    
    try:
        # Import after setting environment variables
        from app.services.google_maps import GoogleMapsService
        
        maps_service = GoogleMapsService()
        
        # Test NYC locations
        origin = "Times Square, New York, NY"  
        destination = "Central Park, New York, NY"
        
        print(f"📍 Testing route: {origin} → {destination}")
        print("🔄 Getting routes and pricing...")
        
        result = await maps_service.get_multi_modal_routes(origin, destination)
        
        print(f"\n✅ Response received!")
        print(f"🚩 Origin: {result['origin']}")
        print(f"🏁 Destination: {result['destination']}")
        print(f"⏰ Timestamp: {result['timestamp']}")
        
        print(f"\n🛣️  Available Routes ({len(result['routes'])} modes):")
        for mode, route_info in result['routes'].items():
            print(f"   • {mode.capitalize()}: {route_info['duration']} ({route_info['distance']})")
        
        print(f"\n💰 Pricing Information:")
        for category, providers in result['pricing'].items():
            print(f"   {category.capitalize()}:")
            for provider, info in providers.items():
                # Handle pricing display
                if info.get('price'):
                    if info.get('price_range'):
                        price_str = info['price_range']
                    else:
                        price_str = f"${info['price']/100:.2f}"
                elif info.get('price') == 0:
                    price_str = "Free"
                else:
                    price_str = "N/A"
                
                duration_str = f"{info['duration']}min" if info['duration'] else "N/A"
                status = info['status']
                service = info.get('service', '')
                
                print(f"      • {provider.capitalize()}: {price_str} | {duration_str} | {status} {service}")
        
        print(f"\n🎉 Integration test successful!")
        print(f"📊 Mock rideshare pricing is working as expected")
        
        return result
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(test_pricing_integration())