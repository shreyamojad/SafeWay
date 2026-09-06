from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class RouteRequest(BaseModel):
    source: str
    destination: str
    preference: str


@app.get("/")
def home():
    return {"message": "SafeWay Backend is running!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/route")
def calculate_route(request: RouteRequest):
    return {
        "source": request.source,
        "destination": request.destination,
        "preference": request.preference,
        "message": "Route request received successfully"
    }