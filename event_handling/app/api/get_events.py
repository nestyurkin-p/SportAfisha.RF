from pydantic import BaseModel, UUID4
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from starlette import status
from app.data.db import get_db
from app.data.events import Event
from app import oauth


router = APIRouter()


class EventResponse(BaseModel):
    id: UUID4
    title: str
    age_group: str
    females: bool
    males: bool
    discipline: str
    results: dict | None
    date_start: date
    date_finished: date
    location: str
    description: str
    is_local: bool

    pending: bool
    rejected: bool
    confirmed: bool
    finished: bool

    class Config:
        orm_mode = True


@router.get("/get_events", response_model=list[EventResponse])
def get_events(db: Session = Depends(get_db)):
    events = db.query(Event).all()
    return events


@router.get("/ping")
async def ping(token: str):
    await oauth.validate(token, [oauth.Role.superuser])
    return "pong"
