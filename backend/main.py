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


def calculate_safety_score(route_index):
    # Temporary prototype safety factors
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

    # Temporarily make different routes have different scores
    safety_score = safety_score - (route_index * 12)

    return round(safety_score, 2)


def generate_safety_explanation():
    return {
        "crime": "Low crime risk",
        "lighting": "Good street lighting",
        "traffic": "Moderate traffic",
        "crowd": "Good crowd activity",
        "overall": "This route has a relatively good safety profile."
    }


@app.get("/")
def home():
    return {
        "message": "SafeWay Backend is running!"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post("/route")
async def calculate_route(request: RouteRequest):

    # OSRM routing service
    url = (
        f"https://router.project-osrm.org/route/v1/driving/"
        f"{request.source_lon},{request.source_lat};"
        f"{request.destination_lon},{request.destination_lat}"
        f"?overview=full&geometries=geojson&alternatives=true"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code != 200:
        return {
            "error": "Unable to get route"
        }

    route_data = response.json()

    routes = []

    # Process every route returned by OSRM
    for route_index, route in enumerate(route_data["routes"]):

        safety_score = calculate_safety_score(route_index)

        routes.append({
            "route_index": route_index,
            "distance_km": round(route["distance"] / 1000, 2),
            "duration_minutes": round(route["duration"] / 60, 2),
            "safety_score": safety_score,
            "geometry": route["geometry"],
            "safety_explanation": generate_safety_explanation()
        })

    # Find the route with the highest safety score
    safest_route_index = max(
        range(len(routes)),
        key=lambda i: routes[i]["safety_score"]
    )

    return {
        "preference": request.preference,
        "routes": routes,
        "recommended_route_index": safest_route_index,
        "recommended_route": routes[safest_route_index]
    }