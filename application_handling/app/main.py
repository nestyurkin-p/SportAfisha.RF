import asyncio
import logging
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitQueue
from data.models import CreateApplicationRequest, ProcessApplicationRequest
from data.database import get_db, create_applications_table
from data.application import Application

logging.basicConfig(level=logging.INFO)

api = FastAPI()
broker = RabbitBroker("amqp://root:toor@rabbitmq:5672/")
app = FastStream(broker)


@api.post("/create_application")
async def create_application(
        request: CreateApplicationRequest, db: Session = Depends(get_db)
):
    new_application = Application(
        event_id=request.event_id,
        application_purpose=request.application_purpose,  # open / close
        creator_id=request.creator_id,
        results=request.results,
    )
    try:
        db.add(new_application)
        db.commit()
        db.refresh(new_application)
        application_dict = new_application.to_dict()
        await broker.publish(application_dict, queue="pending-events-queue")
        data_to_return = {"status": "success", "application_id": new_application.application_id}
        return data_to_return
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@api.post("/process_application")
async def process_application(
        request: ProcessApplicationRequest, db: Session = Depends(get_db)
):
    try:
        application = (
            db.query(Application)
            .filter(Application.application_id == request.application_id)
            .first()
        )

        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        application.pending = request.pending
        application.confirmed = request.confirmed
        application.rejected = request.rejected

        db.add(application)
        db.commit()
        db.refresh(application)
        application_dict = application.to_dict()

        # условия разделения на открытие и закрытие заявки в другом микросервисе
        # тк глобально их логика совпадает до отправки, отличаются только application.purpose
        if application.rejected:  # Шаг 3: заявка отклонена
            await broker.publish(application_dict, queue="rejected-events-queue")
        elif application.confirmed:  # Шаг 3: заявка подтверждена
            await broker.publish(application_dict, queue="confirmed-events-queue")
        return application_dict
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.after_startup
async def startup():
    await broker.declare_queue(RabbitQueue("pending-events-queue"))
    await broker.declare_queue(RabbitQueue("rejected-events-queue"))
    await broker.declare_queue(RabbitQueue("confirmed-events-queue"))


async def start_faststream():
    await app.run()


async def start_fastapi():
    config = uvicorn.Config(api, host="0.0.0.0", port=8002)
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    await asyncio.gather(start_fastapi(), start_faststream())


if __name__ == "__main__":
    create_applications_table()
    asyncio.run(main())
