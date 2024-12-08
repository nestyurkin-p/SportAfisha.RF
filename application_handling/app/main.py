import asyncio
import logging
from sqlalchemy.orm.attributes import Event
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitQueue
from data.models import CreateApplicationRequest, ProcessApplicationRequest
from data.database import get_db, create_applications_table
from data.application import Application
from broker import broker

import oauth

logging.basicConfig(level=logging.INFO)

api = FastAPI()
app = FastStream(broker)


@api.get("/get_applications")
async def get_application(token: str, db: Session = Depends(get_db)):
    await oauth.validate(token, [])
    applications = db.query(Application).all()
    return applications


@api.post("/upload_application")
async def upload_application(
    request: CreateApplicationRequest, token: str, db: Session = Depends(get_db)
):
    await oauth.validate(token, [oauth.Role.office])
    application = (
        db.query(Application).filter(request.event_id == Application.event_id).first()
    )
    if application and application.rejected and application.purpose == request.purpose:
        application.results = request.results
        application.pending = True
        application.confirmed = False
        application.rejected = False

        application_dict = application.to_dict()
        application_dict["resend"] = True
        await broker.publish(
            application_dict, queue=f"{application.purpose}-events-queue"
        )

        db.commit()

        data_to_return = {
            "status": "success",
            "application_id": application.id,
            "resend": True,
        }
        return data_to_return

    new_application = Application(
        event_id=request.event_id,
        purpose=request.purpose,  # open / close
        creator_id=request.creator_id,
        results=request.results,
    )
    try:
        db.add(new_application)
        db.commit()
        db.refresh(new_application)
        application_dict = new_application.to_dict()
        await broker.publish(application_dict, queue=f"{request.purpose}-events-queue")
        data_to_return = {
            "status": "success",
            "application_id": new_application.id,
        }
        return data_to_return
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@api.post("/process_application")
async def process_application(
    request: ProcessApplicationRequest, token: str, db: Session = Depends(get_db)
):
    await oauth.validate(token, [oauth.Role.office])
    try:
        application = (
            db.query(Application)
            .filter(Application.id == request.application_id)
            .first()
        )

        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        application.pending = request.pending
        application.confirmed = request.confirmed
        application.rejected = request.rejected

        # db.add(application)
        db.commit()
        db.refresh(application)
        application_dict = application.to_dict()

        # условия разделения на открытие и закрытие заявки в другом микросервисе
        # тк глобально их логика совпадает до отправки, отличаются только application.purpose
        if "open" == application.purpose:  # Шаг 3: заявка отклонена
            await broker.publish(application_dict, queue="open-events-queue")
        if "close" == application.purpose:  # Шаг 3: заявка отклонена
            await broker.publish(application_dict, queue="close-events-queue")

        return application_dict
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.after_startup
async def startup():
    await broker.declare_queue(RabbitQueue("open-events-queue"))
    await broker.declare_queue(RabbitQueue("close-events-queue"))


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
