import asyncio
import logging
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from faststream import FastStream
from faststream.rabbit import RabbitQueue
from data.models import ProcessApplicationRequest
from data.database import get_db, create_applications_table
from data.application import Application
from routers.create_application import create_application_router


logging.basicConfig(level=logging.INFO)

api = FastAPI()
app = FastStream(broker)

api.include_router(create_application_router)

@api.post("/process_application")
async def process_application(
    request: ProcessApplicationRequest, db: Session = Depends(get_db)
):
    try:
        application = (
            db.query(Application)
            .filter(Application.id == request.application_id)
            .first()
        )

        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        application.approved = request.approved
        db.commit()
        db.refresh(application)
        data_to_return = {
            "status": "success",
            "application_id": application.id,
            "approved": application.approved,
        }
        await broker.publish(data_to_return, queue="application-handling-queue")
        return data_to_return
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.after_startup
async def startup():
    # await broker.declare_queue(RabbitQueue("test-queue"))
    await broker.declare_queue(RabbitQueue("application-handling-queue"))
    await broker.publish("Hello World!", queue="application-handling-queue")


# @broker.subscriber("test-queue")
@broker.subscriber("application-handling-queue")
async def base_handler(body):
    logging.info(f"Got message: {body}")


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
