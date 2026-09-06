from fastapi import FastAPI
from pydantic import BaseModel, field_validator
import httpx

app = FastAPI()


class RouteRequest(BaseModel):
    source_lat: float
    source_lon: float
    destination_lat: float
    destination_lon: float
    preference: str

    @field_validator("preference")
    @classmethod
    def validate_preference(cls, value):
        value = value.lower()

        allowed_preferences = [
            "fastest",
            "balanced",
            "safest"
        ]

        if value not in allowed_preferences:
            raise ValueError(
                "Preference must be fastest, balanced, or safest"
            )

        return value

    @field_validator("source_lat", "destination_lat")
    @classmethod
    def validate_latitude(cls, value):
        if value < -90 or value > 90:
            raise ValueError(
                "Latitude must be between -90 and 90"
            )

        return value

    @field_validator("source_lon", "destination_lon")
    @classmethod
    def validate_longitude(cls, value):
        if value < -180 or value > 180:
            raise ValueError(
                "Longitude must be between -180 and 180"
            )

        return value


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

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)

        if response.status_code != 200:
            return {
                "error": "Routing service returned an error",
                "status_code": response.status_code
            }

        route_data = response.json()

    except httpx.RequestError:
        return {
            "error": "Unable to connect to routing service"
        }

    # Check if OSRM found any routes
    if route_data.get("code") != "Ok":
        return {
            "error": "No route could be found for the given locations"
        }

    if not route_data.get("routes"):
        return {
            "error": "No routes available"
        }

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

    # User preference
    preference = request.preference

    if preference == "fastest":

        recommended_route_index = min(
            range(len(routes)),
            key=lambda i: routes[i]["duration_minutes"]
        )

    elif preference == "balanced":

        # 60% safety + 40% travel time
        max_duration = max(
            route["duration_minutes"] for route in routes
        )

        for route in routes:

            if max_duration == 0:
                time_score = 100
            else:
                time_score = (
                    1 - route["duration_minutes"] / max_duration
                ) * 100

            route["balanced_score"] = round(
                route["safety_score"] * 0.60
                + time_score * 0.40,
                2
            )

        recommended_route_index = max(
            range(len(routes)),
            key=lambda i: routes[i]["balanced_score"]
        )

    else:
        # Safest
        recommended_route_index = max(
            range(len(routes)),
            key=lambda i: routes[i]["safety_score"]
        )

    return {
        "preference": preference,
        "routes": routes,
        "recommended_route_index": recommended_route_index,
        "recommended_route": routes[recommended_route_index]
    }