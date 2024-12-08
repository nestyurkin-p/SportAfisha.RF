import json
from datetime import date, datetime
import logging
from pydantic import UUID4, BaseModel, Json
from typing import Optional
from app.api.get_events import EventResponse
from app.data.events import Event
from app.data import db
from faststream.rabbit import RabbitBroker

broker = RabbitBroker("amqp://root:toor@rabbitmq:5672/")


class ApplicationStatus(BaseModel):
    pending: bool
    rejected: bool
    confirmed: bool


class EventStatusChanger(BaseModel):
    event_id: str
    creator_id: str
    application_id: str
    purpose: str
    application_status: ApplicationStatus
    results: dict | None
    resend: Optional[bool] = None


@broker.subscriber("close-events-queue")
async def processing_close_event(msg: EventStatusChanger):
    with db.session() as db_sess:
        event = db_sess.query(Event).filter(Event.id == msg.event_id).first()
        if not event:
            logging.error(f"Can't find event with id={msg.event_id}")
            raise Exception

        if bool(event.is_local):
            logging.error("This event dosen't need approve, because this event local")
            raise Exception

        if msg.application_status.confirmed:
            event.finished = True
        elif msg.resend:
            event.confirmed = False
            event.pending = True
            event.rejected = False
        elif msg.application_status.rejected:
            event.confirmed = False
            event.pending = False
            event.rejected = True
        db_sess.commit()

@broker.subscriber("open-events-queue")
async def processing_open_event(msg: EventStatusChanger):
    with db.session() as db_sess:
        event = db_sess.query(Event).filter(Event.id == msg.event_id).first()
        if not event:
            logging.error(f"Can't find event with id={msg.event_id}")
            raise Exception

        if bool(event.is_local):
            logging.error("This event dosen't need approve, because this event local")
            raise Exception

        if msg.resend:
            event.pending = True
            event.rejected = False
            event.confirmed = False
            event.finished = False
        else:
            event.pending = msg.application_status.pending
            event.rejected = msg.application_status.rejected
            event.confirmed = msg.application_status.confirmed
            event.finished = False
        db_sess.commit()


@broker.subscriber("statistics-event-request-queue")
async def wait_events(body):
    with db.session() as db_sess:
        events = db_sess.query(Event).all()

    # TODO: refactor this facking shit with pydantic
    event_responses = [
        EventResponse(
            id=event.id,
            title=str(event.title),
            age_group=str(event.age_group),
            females=bool(event.females),
            males=bool(event.males),
            is_approved=bool(event.is_approved),
            discipline=str(event.discipline),
            results=event.results,
            date_start=event.date_start,
            date_finished=event.date_finished,
            location=str(event.location),
            description=str(event.description),
            is_local=bool(event.is_local),
        )
        for event in events
        for event in events
    ]

    await broker.publish(event_responses, "statistics-event-response-queue")
