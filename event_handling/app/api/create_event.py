from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.data.events import Event
from app.data.db import get_db
from pydantic import BaseModel
from datetime import date
from typing import Optional
from app import oauth

router = APIRouter()


class EventCreate(BaseModel):
    title: str
    age_group: str
    females: bool
    males: bool
    discipline: str
    results: Optional[dict] = None
    date_start: date
    date_finished: date
    location: str
    description: str
    is_local: bool


@router.post("/create_event", response_model=dict)
async def create_event(
    event_data: EventCreate, token: str, db: Session = Depends(get_db)
):
    await oauth.validate(token, [oauth.Role.superuser])
    existing_event = db.query(Event).filter(Event.title == event_data.title).first()
    if existing_event:
        raise HTTPException(
            status_code=400, detail="Event with this title already exists."
        )

    new_event = Event(
        title=event_data.title,
        age_group=event_data.age_group,
        females=event_data.females,
        males=event_data.males,
        discipline=event_data.discipline,
        results=event_data.results,
        date_start=event_data.date_start,
        date_finished=event_data.date_finished,
        location=event_data.location,
        description=event_data.description,
        is_local=event_data.is_local,
    )

    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    return {"message": "Event created successfully", "event_id": new_event.id}
