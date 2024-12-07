import asyncio
import logging
import uvicorn
from fastapi import FastAPI
from faststream import FastStream
from faststream.rabbit import RabbitQueue
from app.data import db
from app.api import api_router
from app.message_broker import broker


logging.basicConfig(level=logging.INFO)

fastapi_app = FastAPI()

app = FastStream(broker)


@app.after_startup
async def startup():
    await broker.declare_queue(RabbitQueue("statistics-event-response-queue"))


async def start_faststream():
    await app.run()


async def start_fastapi():
    fastapi_app.include_router(api_router)
    config = uvicorn.Config(fastapi_app, host="0.0.0.0", port=8004)
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    db.global_init()

    await asyncio.gather(start_fastapi(), start_faststream())


if __name__ == "__main__":
    asyncio.run(main())
