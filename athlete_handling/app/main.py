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
from models import Athlete
from schemas import AthleteCreate, AthleteUpdate, AthleteInDB, StatusResponse


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


@api.post("/create_athlete", response_model=StatusResponse)
async def create_athlete(athlete: AthleteCreate, db: Session = Depends(get_db)):
    logger.info(f"[CREATE] Attempting to create athlete with UIN: {athlete.UIN}")

    new_athlete = Athlete(**athlete.model_dump())
    db.add(new_athlete)
    db.commit()
    db.refresh(new_athlete)

    logger.info(
        f"[CREATE] Athlete created with ID: {new_athlete.id}, UIN: {new_athlete.UIN}"
    )

    return {"status": "OK", "id": new_athlete.id}


@api.post("/update_athlete", response_model=StatusResponse)
async def update_athlete(athlete: AthleteUpdate, db: Session = Depends(get_db)):
    logger.info(f"[UPDATE] Attempting to update athlete with ID: {athlete.id}")

    db_athlete = db.query(Athlete).filter(Athlete.id == athlete.id).first()

    if not db_athlete:
        logger.warning(f"[UPDATE] Athlete with ID {athlete.id} not found.")
        raise HTTPException(status_code=404, detail="Athlete not found")

    update_data = athlete.model_dump()
    update_data.pop("id", None)

    for field, value in update_data.items():
        if value:
            setattr(db_athlete, field, value)

    db.commit()
    db.refresh(db_athlete)

    logger.info(
        f"[UPDATE] Athlete with ID: {db_athlete.id} (UIN: {db_athlete.UIN}) has been updated."
    )

    return {"status": "OK", "id": db_athlete.id}


@api.get("/athletes", response_model=List[AthleteInDB])
async def get_athletes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Возвращает список спортсменов с возможностью пагинации.
    """
    athletes = db.query(Athlete).offset(skip).limit(limit).all()
    logger.info(f"[GET] Retrieved {len(athletes)} athletes from the database.")
    return athletes


@api.get("/athletes/{athlete_id}", response_model=AthleteInDB)
async def get_athlete(athlete_id: UUID, db: Session = Depends(get_db)):
    """
    Возвращает информацию о конкретном спортсмене по его ID.
    """
    athlete = db.query(Athlete).filter(Athlete.id == athlete_id).first()
    if not athlete:
        logger.warning(f"[GET] Athlete with ID {athlete_id} not found.")
        raise HTTPException(status_code=404, detail="Athlete not found")
    logger.info(f"[GET] Retrieved athlete with ID {athlete_id}.")
    return athlete


@app.after_startup
async def startup():

    await broker.declare_queue(RabbitQueue("statistics-athlete-response-queue"))


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
