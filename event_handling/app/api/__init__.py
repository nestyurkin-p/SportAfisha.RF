from fastapi import APIRouter
from app.api import get_events, create_event

api_router = APIRouter()

api_router.include_router(get_events.router, prefix="/api")
api_router.include_router(create_event.router, prefix="/api")
