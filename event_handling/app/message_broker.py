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


class EventApprovedMsg(BaseModel):
    event_id: str
    creator_id: str
    application_id: str
    application_type: str 
    approved: bool
    results: dict | None


@broker.subscriber("finished-events-queue")
async def finish_event(body):
    print(type(body))


@broker.subscriber("approved-events-queue")
async def aprove_event(msg: EventApprovedMsg):
    # {
    #     "event_id": uuid,
    #     "approved_status": bool,
    #     "results": json | none
    # }
    with db.session() as db_sess:
        event = db_sess.query(Event).filter(Event.id == msg.event_id).first()
        print(msg)
        if not event:
            logging.error(f"Can't find event with id={msg.event_id}")
            raise Exception

        if bool(event.is_local):
            logging.error("This event dosen't need approve")
            raise Exception

        event.is_approved = msg.approved
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
            is_local=bool(event.is_local)
        ) for event in events
        for event in events
    ]

    await broker.publish(event_responses, "statistics-event-response-queue")


