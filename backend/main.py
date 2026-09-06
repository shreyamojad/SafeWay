from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home():
    return {"message": "SafeWay Backend is running!"}