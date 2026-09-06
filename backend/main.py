from fastapi import FastAPI
from pydantic import BaseModel, field_validator
import httpx
import pandas as pd
import joblib
from pathlib import Path

app = FastAPI()


# =========================================================
# LOAD MEMBER 2'S TRAINED AI MODEL
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "model" / "saferoute_model.pkl"

model = joblib.load(MODEL_PATH)


# =========================================================
# REQUEST MODEL
# =========================================================

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


# =========================================================
# AI SAFETY PREDICTION
# =========================================================

def predict_safety_score(
    crime_score,
    lighting_score,
    traffic_score,
    crowd_score,
    time_of_day,
    day_of_week,
    road_condition
):

    new_location = pd.DataFrame([{
        "crime_score": crime_score,
        "lighting_score": lighting_score,
        "traffic_score": traffic_score,
        "crowd_score": crowd_score,
        "time_of_day": time_of_day,
        "day_of_week": day_of_week,
        "road_condition": road_condition
    }])

    prediction = model.predict(new_location)

    return round(float(prediction[0]), 2)


# =========================================================
# SAFETY EXPLANATION
# =========================================================

def generate_safety_explanation(
    crime_score,
    lighting_score,
    traffic_score,
    crowd_score
):

    if crime_score >= 70:
        crime = "Low crime risk"
    elif crime_score >= 40:
        crime = "Moderate crime risk"
    else:
        crime = "Higher crime risk"

    if lighting_score >= 70:
        lighting = "Good street lighting"
    elif lighting_score >= 40:
        lighting = "Moderate street lighting"
    else:
        lighting = "Poor street lighting"

    if traffic_score >= 70:
        traffic = "Low traffic"
    elif traffic_score >= 40:
        traffic = "Moderate traffic"
    else:
        traffic = "High traffic"

    if crowd_score >= 70:
        crowd = "Good crowd activity"
    elif crowd_score >= 40:
        crowd = "Moderate crowd activity"
    else:
        crowd = "Low crowd activity"

    return {
        "crime": crime,
        "lighting": lighting,
        "traffic": traffic,
        "crowd": crowd,
        "overall": "Safety prediction generated using the AI model."
    }


# =========================================================
# HOME API
# =========================================================

@app.get("/")
def home():
    return {
        "message": "SafeWay Backend is running!"
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# =========================================================
# ROUTE API
# =========================================================

@app.post("/route")
async def calculate_route(request: RouteRequest):

    # -----------------------------------------------------
    # TEMPORARY SAFETY INPUTS
    # -----------------------------------------------------

    crime_score = 80
    lighting_score = 85
    traffic_score = 75
    crowd_score = 80

    time_of_day = 18
    day_of_week = 3

    road_condition = 85


    # -----------------------------------------------------
    # OSRM ROUTING SERVICE
    # -----------------------------------------------------

    url = (
        f"https://router.project-osrm.org/route/v1/driving/"
        f"{request.source_lon},{request.source_lat};"
        f"{request.destination_lon},{request.destination_lat}"
        f"?overview=full&geometries=geojson&alternatives=true"
    )


    # -----------------------------------------------------
    # CALL OSRM
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # CHECK ROUTE RESULT
    # -----------------------------------------------------

    if route_data.get("code") != "Ok":
        return {
            "error": "No route could be found for the given locations"
        }

    if not route_data.get("routes"):
        return {
            "error": "No routes available"
        }


    # -----------------------------------------------------
    # PROCESS ROUTES
    # -----------------------------------------------------

    routes = []

    for route_index, route in enumerate(route_data["routes"]):

        # AI MODEL PREDICTION

        safety_score = predict_safety_score(
            crime_score,
            lighting_score,
            traffic_score,
            crowd_score,
            time_of_day,
            day_of_week,
            road_condition
        )


        # Temporary difference between routes
        # Will later be replaced by route-specific data.

        safety_score = max(
            0,
            safety_score - (route_index * 5)
        )


        routes.append({

            "route_index": route_index,

            "distance_km": round(
                route["distance"] / 1000,
                2
            ),

            "duration_minutes": round(
                route["duration"] / 60,
                2
            ),

            "safety_score": safety_score,

            "geometry": route["geometry"],

            "safety_explanation":
                generate_safety_explanation(
                    crime_score,
                    lighting_score,
                    traffic_score,
                    crowd_score
                )
        })


    # =====================================================
    # ROUTE RECOMMENDATION
    # =====================================================

    preference = request.preference


    # -----------------------------------------------------
    # FASTEST
    # -----------------------------------------------------

    if preference == "fastest":

        recommended_route_index = min(
            range(len(routes)),
            key=lambda i:
                routes[i]["duration_minutes"]
        )


    # -----------------------------------------------------
    # BALANCED
    # -----------------------------------------------------

    elif preference == "balanced":

        max_duration = max(
            route["duration_minutes"]
            for route in routes
        )

        for route in routes:

            if max_duration == 0:

                time_score = 100

            else:

                time_score = (
                    1
                    - route["duration_minutes"]
                    / max_duration
                ) * 100


            route["balanced_score"] = round(

                route["safety_score"] * 0.60
                +
                time_score * 0.40,

                2
            )


        recommended_route_index = max(
            range(len(routes)),
            key=lambda i:
                routes[i]["balanced_score"]
        )


    # -----------------------------------------------------
    # SAFEST
    # -----------------------------------------------------

    else:

        recommended_route_index = max(
            range(len(routes)),
            key=lambda i:
                routes[i]["safety_score"]
        )


    # =====================================================
    # FINAL RESPONSE
    # =====================================================

    return {

        "preference": preference,

        "routes": routes,

        "recommended_route_index":
            recommended_route_index,

        "recommended_route":
            routes[recommended_route_index]
    }