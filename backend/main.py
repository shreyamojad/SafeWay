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

    return {
        "preference": request.preference,
        "routes": route_data["routes"]
    }