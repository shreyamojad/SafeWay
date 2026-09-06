from fastapi import FastAPI
from pydantic import BaseModel
import httpx

app = FastAPI()


class RouteRequest(BaseModel):
    source_lat: float
    source_lon: float
    destination_lat: float
    destination_lon: float
    preference: str


def calculate_safety_score():
    # Temporary prototype values
    crime_score = 80
    lighting_score = 85
    traffic_score = 75
    crowd_score = 80

    safety_score = (
        crime_score * 0.35
        + lighting_score * 0.25
        + traffic_score * 0.20
        + crowd_score * 0.20
    )

    return round(safety_score, 2)


@app.get("/")
def home():
    return {"message": "SafeWay Backend is running!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/route")
async def calculate_route(request: RouteRequest):

    url = (
        f"https://router.project-osrm.org/route/v1/driving/"
        f"{request.source_lon},{request.source_lat};"
        f"{request.destination_lon},{request.destination_lat}"
        f"?overview=false&alternatives=true"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code != 200:
        return {"error": "Unable to get route"}

    route_data = response.json()

    safety_score = calculate_safety_score()

    routes = []

    for route in route_data["routes"]:
        routes.append({
            "distance_km": round(route["distance"] / 1000, 2),
            "duration_minutes": round(route["duration"] / 60, 2),
            "safety_score": safety_score
        })

    return {
        "preference": request.preference,
        "routes": routes
    }