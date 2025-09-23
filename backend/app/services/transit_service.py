"""
Public Transit Service - NYC MTA Integration via Google Maps Transit API
Handles subway, bus, and rail transit options with real-time data.
"""
import os
import httpx
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class TransitService:
    """Service for NYC public transit information via Google Maps Transit API."""

    # NYC MTA Pricing (as of 2024)
    SUBWAY_FARE = 2.90  # Base fare
    BUS_FARE = 2.90     # Base fare
    EXPRESS_BUS_FARE = 7.00

    def __init__(self):
        self.api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_MAPS_API_KEY not found in environment variables")

        self.base_url = "https://maps.googleapis.com/maps/api"

    async def get_transit_directions(
        self,
        origin: str,
        destination: str,
        departure_time: Optional[str] = "now",
        mode: str = "transit"
    ) -> Dict[str, Any]:
        """
        Get comprehensive transit directions with multiple route options.

        Args:
            origin: Starting location address
            destination: Ending location address
            departure_time: When to depart (default: "now")
            mode: Transportation mode (default: "transit")

        Returns:
            Dictionary containing transit routes with detailed information
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                routes = await self._fetch_transit_routes(
                    client, origin, destination, departure_time
                )

                if not routes:
                    return self._create_unavailable_response(origin, destination)

                # Process and structure the routes
                processed_routes = []
                for idx, route in enumerate(routes[:3]):  # Top 3 routes
                    processed_route = self._process_transit_route(route, idx)
                    if processed_route:
                        processed_routes.append(processed_route)

                return {
                    "status": "available",
                    "origin": origin,
                    "destination": destination,
                    "routes": processed_routes,
                    "route_count": len(processed_routes),
                    "timestamp": datetime.now().isoformat(),
                    "provider": "NYC MTA"
                }

        except Exception as e:
            logger.error(f"Error getting transit directions: {str(e)}")
            return self._create_error_response(origin, destination, str(e))

    async def _fetch_transit_routes(
        self,
        client: httpx.AsyncClient,
        origin: str,
        destination: str,
        departure_time: str
    ) -> Optional[List[Dict]]:
        """Fetch transit routes from Google Maps API."""
        url = f"{self.base_url}/directions/json"

        params = {
            'origin': origin,
            'destination': destination,
            'mode': 'transit',
            'alternatives': True,  # Get multiple route options
            'transit_mode': 'subway|bus|rail',  # NYC transit modes
            'key': self.api_key
        }

        # Add departure time if specified
        if departure_time and departure_time != "now":
            params['departure_time'] = departure_time
        else:
            params['departure_time'] = 'now'

        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get('status') != 'OK':
                logger.warning(f"Transit API returned status: {data.get('status')}")
                return None

            return data.get('routes', [])

        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching transit routes: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error fetching transit routes: {str(e)}")
            return None

    def _process_transit_route(self, route: Dict, route_index: int) -> Optional[Dict]:
        """Process a single transit route into structured format."""
        try:
            leg = route['legs'][0]

            # Extract basic route info
            route_info = {
                "route_id": route_index,
                "summary": route.get('summary', 'Transit Route'),
                "distance": leg['distance']['text'],
                "distance_meters": leg['distance']['value'],
                "duration": leg['duration']['text'],
                "duration_minutes": round(leg['duration']['value'] / 60),
                "start_address": leg['start_address'],
                "end_address": leg['end_address'],
                "departure_time": leg.get('departure_time', {}).get('text', 'Now'),
                "arrival_time": leg.get('arrival_time', {}).get('text', 'N/A'),
            }

            # Extract transit steps (subway, bus, walking)
            steps = self._extract_transit_steps(leg.get('steps', []))
            route_info['steps'] = steps
            route_info['total_steps'] = len(steps)

            # Calculate pricing based on transit types used
            pricing = self._calculate_transit_pricing(steps)
            route_info['pricing'] = pricing

            # Identify transit lines used
            transit_lines = self._extract_transit_lines(steps)
            route_info['transit_lines'] = transit_lines

            # Add convenience metrics
            route_info['transfers'] = self._count_transfers(steps)
            route_info['walking_distance'] = self._calculate_walking_distance(steps)

            return route_info

        except Exception as e:
            logger.error(f"Error processing transit route: {str(e)}")
            return None

    def _extract_transit_steps(self, steps: List[Dict]) -> List[Dict]:
        """Extract and format transit steps from route."""
        formatted_steps = []

        for step in steps:
            travel_mode = step.get('travel_mode', 'UNKNOWN')

            step_info = {
                "mode": travel_mode.lower(),
                "distance": step['distance']['text'],
                "duration": step['duration']['text'],
                "instructions": step.get('html_instructions', ''),
            }

            # Add transit-specific details
            if travel_mode == 'TRANSIT':
                transit_details = step.get('transit_details', {})
                step_info['transit'] = {
                    "line_name": transit_details.get('line', {}).get('name', 'Unknown'),
                    "line_short_name": transit_details.get('line', {}).get('short_name', ''),
                    "vehicle_type": transit_details.get('line', {}).get('vehicle', {}).get('type', ''),
                    "departure_stop": transit_details.get('departure_stop', {}).get('name', ''),
                    "arrival_stop": transit_details.get('arrival_stop', {}).get('name', ''),
                    "num_stops": transit_details.get('num_stops', 0),
                    "headsign": transit_details.get('headsign', ''),
                }

            formatted_steps.append(step_info)

        return formatted_steps

    def _calculate_transit_pricing(self, steps: List[Dict]) -> Dict[str, Any]:
        """
        Calculate transit pricing based on steps.
        NYC MTA uses flat-rate pricing: one fare covers a complete trip including transfers.
        """
        has_transit = any(step['mode'] == 'transit' for step in steps)
        has_express_bus = any(
            step.get('transit', {}).get('vehicle_type') == 'BUS' and
            'express' in step.get('transit', {}).get('line_name', '').lower()
            for step in steps if step['mode'] == 'transit'
        )

        if has_express_bus:
            fare = self.EXPRESS_BUS_FARE
            fare_type = "Express Bus"
        elif has_transit:
            fare = self.SUBWAY_FARE
            fare_type = "Standard Fare"
        else:
            fare = 0.0
            fare_type = "Free (Walking Only)"

        return {
            "total_fare": fare,
            "fare_type": fare_type,
            "currency": "USD",
            "note": "Single ride fare (includes free transfers within 2 hours)"
        }

    def _extract_transit_lines(self, steps: List[Dict]) -> List[str]:
        """Extract list of transit lines used in route."""
        lines = []
        for step in steps:
            if step['mode'] == 'transit':
                transit_info = step.get('transit', {})
                line_name = transit_info.get('line_short_name') or transit_info.get('line_name')
                if line_name and line_name not in lines:
                    lines.append(line_name)
        return lines

    def _count_transfers(self, steps: List[Dict]) -> int:
        """Count number of transfers in the route."""
        transit_steps = [s for s in steps if s['mode'] == 'transit']
        # Number of transfers = number of transit legs - 1
        return max(0, len(transit_steps) - 1)

    def _calculate_walking_distance(self, steps: List[Dict]) -> str:
        """Calculate total walking distance."""
        walking_meters = sum(
            int(step.get('distance', '0 m').split()[0])
            for step in steps if step['mode'] == 'walking'
        )

        if walking_meters > 1000:
            return f"{walking_meters / 1000:.1f} km"
        return f"{walking_meters} m"

    def _create_unavailable_response(self, origin: str, destination: str) -> Dict:
        """Create response when transit is not available."""
        return {
            "status": "unavailable",
            "origin": origin,
            "destination": destination,
            "routes": [],
            "route_count": 0,
            "message": "No public transit routes available for this trip",
            "timestamp": datetime.now().isoformat(),
            "provider": "NYC MTA"
        }

    def _create_error_response(self, origin: str, destination: str, error: str) -> Dict:
        """Create error response."""
        return {
            "status": "error",
            "origin": origin,
            "destination": destination,
            "routes": [],
            "route_count": 0,
            "error": error,
            "timestamp": datetime.now().isoformat(),
            "provider": "NYC MTA"
        }

    async def get_transit_summary(
        self,
        origin: str,
        destination: str
    ) -> Dict[str, Any]:
        """
        Get a simplified transit summary for quick comparison.

        Returns best route with essential information.
        """
        transit_data = await self.get_transit_directions(origin, destination)

        if transit_data['status'] != 'available' or not transit_data['routes']:
            return {
                "available": False,
                "fare": None,
                "duration": None,
                "distance": None
            }

        # Get the first (best) route
        best_route = transit_data['routes'][0]

        return {
            "available": True,
            "fare": best_route['pricing']['total_fare'],
            "duration": best_route['duration'],
            "duration_minutes": best_route['duration_minutes'],
            "distance": best_route['distance'],
            "transit_lines": best_route['transit_lines'],
            "transfers": best_route['transfers'],
            "summary": best_route['summary']
        }


# Test function
async def test_transit_service():
    """Test the transit service with NYC locations."""
    print("🚇 Testing NYC Transit Service\n")

    try:
        service = TransitService()

        # Test with popular NYC locations
        origin = "Times Square, Manhattan, NY"
        destination = "Brooklyn Bridge, Brooklyn, NY"

        print(f"📍 Route: {origin} → {destination}\n")

        # Get full transit directions
        result = await service.get_transit_directions(origin, destination)

        print(f"Status: {result['status']}")
        print(f"Provider: {result.get('provider')}")
        print(f"Available Routes: {result.get('route_count', 0)}\n")

        if result['routes']:
            for route in result['routes']:
                print(f"Route {route['route_id'] + 1}: {route['summary']}")
                print(f"  Duration: {route['duration']}")
                print(f"  Distance: {route['distance']}")
                print(f"  Fare: ${route['pricing']['total_fare']:.2f} ({route['pricing']['fare_type']})")
                print(f"  Transit Lines: {', '.join(route['transit_lines'])}")
                print(f"  Transfers: {route['transfers']}")
                print(f"  Walking: {route['walking_distance']}")
                print(f"  Departure: {route['departure_time']} → Arrival: {route['arrival_time']}")
                print()

        # Test summary endpoint
        print("\n📊 Transit Summary:")
        summary = await service.get_transit_summary(origin, destination)
        print(summary)

        print("\n✅ Transit service test complete!")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_transit_service())
