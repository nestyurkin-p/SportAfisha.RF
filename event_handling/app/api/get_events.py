from typing import Optional
from datetime import datetime
from pydantic import BaseModel, UUID4
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date

from app.data.db import get_db
from app.data.events import Event


router = APIRouter()

class EventRequest(BaseModel):
    start_date: datetime
    end_date: datetime
    office_id: Optional[UUID4] = None


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
    creator_id: UUID4

    pending: bool
    rejected: bool
    confirmed: bool
    finished: bool

    class Config:
        orm_mode = True


@router.post("/get_events", response_model=dict[datetime, list[EventResponse]])
def get_events(event_data: EventRequest, db: Session = Depends(get_db)):
    if event_data.office_id:
        events = db.query(Event).filter(
                Event.date_start >= event_data.start_date.date(),  
                Event.date_finished <= event_data.end_date.date(),
                Event.creator_id == event_data.office_id  
            ).all()
    else:
        events = db.query(Event).filter(
                Event.date_start >= event_data.start_date.date(),  
                Event.date_finished <= event_data.end_date.date(),
            ).all()

    grouped_events = {}

    for event in events:
        key = event.date_start
        if key in grouped_events:
            grouped_events[key].append(event)
        else:
            grouped_events[key] = [event, ]

    return grouped_events



@router.get("/ping")
async def ping():
    return "pong"
