from app.main import api


@api.get("/get_events")
async def get_events():
    return {"message": "Hello from FastAPI"}

