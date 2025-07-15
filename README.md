# NYC Transportation Optimizer

A web application that compares transportation options across all modes (rideshare, public transit, bikes, scooters) for trips in New York City, helping users make optimal decisions based on real-time cost, time, and convenience.

## Features

- Real-time pricing for Uber (UberX, Bike, Scooter) and Lyft (Standard, Bike, Scooter)
- Google Maps integration for route calculation and transit directions
- Side-by-side comparison of all transportation options
- Responsive React frontend with FastAPI backend

## Tech Stack

**Backend:** FastAPI, Python 3.11+, httpx
**Frontend:** React 18.2, Axios, React Router
**APIs:** Google Maps Platform, Uber API, Lyft API

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 16+
- API keys for Google Maps, Uber, and Lyft

### Installation

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/app/.env`:
```env
GOOGLE_MAPS_API_KEY=your_key
UBER_CLIENT_ID=your_key
UBER_CLIENT_SECRET=your_secret
UBER_SERVER_TOKEN=your_token
LYFT_CLIENT_ID=your_key
LYFT_CLIENT_SECRET=your_secret
```

Run server:
```bash
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm start
```

Application runs at `http://localhost:3000`
API documentation at `http://localhost:8000/docs`

## API Usage

```bash
POST http://localhost:8000/api/v1/routes/compare
Content-Type: application/json

{
  "origin": "Times Square, New York, NY",
  "destination": "Brooklyn Bridge, New York, NY"
}
```

## License

MIT
