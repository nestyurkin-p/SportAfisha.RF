from pydantic import BaseModel, UUID4
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date
from app.data.db import get_db
from app.data.events import Event


router = APIRouter()


class EventResponse(BaseModel):
    id: UUID4
    title: str
    age_group: str
    females: bool
    males: bool
    is_approved: bool
    discipline: str
    results: dict | None
    date_start: date
    date_finished: date
    location: str
    description: str
    is_local: bool

    class Config:
        orm_mode = True 


@router.get("/get_events", response_model=list[EventResponse])
def get_events(db: Session = Depends(get_db)):
    events = db.query(Event).all()
    return events 


@router.get("/ping")
def ping():
    return "pong"

