import asyncio
import logging
import os
from typing import List

import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitQueue
from sqlalchemy.orm import Session
from uuid import UUID

from database import Base, engine, get_db
from models import Office
from schemas import OfficeCreate, OfficeUpdate, OfficeInDB, StatusResponse, OfficeDelete


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api = FastAPI()


RABBIT_URL = os.getenv("RABBIT_URL", "amqp://root:toor@rabbitmq:5672/")
broker = RabbitBroker(RABBIT_URL)


app = FastStream(broker)


Base.metadata.create_all(bind=engine)


@api.get("/ping")
async def ping():
    return "pong"


@api.post("/create_office", response_model=StatusResponse)
async def create_office(office: OfficeCreate, db: Session = Depends(get_db)):

    new_office = Office(**office.model_dump())
    db.add(new_office)
    db.commit()
    db.refresh(new_office)

    return {"status": "OK", "id": new_office.id}


@api.post("/update_office", response_model=StatusResponse)
async def update_office(office: OfficeUpdate, db: Session = Depends(get_db)):
    logger.info(f"[UPDATE] Attempting to update office with ID: {office.id}")

    db_office = db.query(Office).filter(Office.id == office.id).first()

    if not db_office:
        logger.warning(f"[UPDATE] Office with ID {office.id} not found.")
        raise HTTPException(status_code=404, detail="Office not found")

    update_data = office.model_dump()
    update_data.pop("id", None)

    for field, value in update_data.items():
        if value:
            setattr(db_office, field, value)

    db.commit()
    db.refresh(db_office)

    logger.info(f"[UPDATE] Office with ID: {db_office.id} has been updated.")

    return {"status": "OK", "id": db_office.id}


@api.post("/delete_office", response_model=StatusResponse)
async def delete_office(office: OfficeDelete, db: Session = Depends(get_db)):
    logger.info(f"[DELETE] Attempting to delete office with ID: {office.id}")

    db_office = db.query(Office).filter(Office.id == office.id).first()

    if not db_office:
        logger.warning(f"[DELETE] Office with ID {office.id} not found.")
        raise HTTPException(status_code=404, detail="Office not found")

    db.delete(db_office)
    db.commit()

    logger.info(f"[DELETE] Office with ID: {office.id} has been deleted.")

    return {"status": "OK", "id": office.id}


@api.get("/offices", response_model=List[OfficeInDB])
async def get_offices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Возвращает список offices с возможностью пагинации.
    """
    offices = db.query(Office).offset(skip).limit(limit).all()
    logger.info(f"[GET] Retrieved {len(offices)} offices from the database.")
    return offices


@api.get("/offices/{office_id}", response_model=OfficeInDB)
async def get_office(office_id: UUID, db: Session = Depends(get_db)):
    """
    Возвращает информацию о конкретном office по его ID.
    """
    office = db.query(Office).filter(Office.id == office_id).first()
    if not office:
        logger.warning(f"[GET] Office with ID {office_id} not found.")
        raise HTTPException(status_code=404, detail="Office not found")
    logger.info(f"[GET] Retrieved athlete with ID {office_id}.")
    return office


@app.after_startup
async def startup():
    await broker.declare_queue(RabbitQueue("statistics-office-response-queue"))


async def start_faststream():
    await app.run()


async def start_fastapi():
    config = uvicorn.Config(api, host="0.0.0.0", port=8003, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    await asyncio.gather(start_fastapi(), start_faststream())


if __name__ == "__main__":
    asyncio.run(main())
