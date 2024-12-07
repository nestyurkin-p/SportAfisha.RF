import asyncio
import logging
import uvicorn
from fastapi import FastAPI
from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitQueue

logging.basicConfig(level=logging.INFO)

api = FastAPI()
broker = RabbitBroker("amqp://root:toor@rabbitmq:5672/")
app = FastStream(broker)


@api.get("/")
async def read_root():
    return {"message": "Hello from FastAPI"}


@app.after_startup
async def startup():
    await broker.declare_queue(RabbitQueue("test-queue"))
    await broker.publish("Hello World!", queue="test-queue")


@broker.subscriber("test-queue")
async def base_handler(body):
    logging.info(f"Got message: {body}")


async def start_faststream():
    await app.run()


async def start_fastapi():
    config = uvicorn.Config(api, host="0.0.0.0", port=8003)
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    await asyncio.gather(start_fastapi(), start_faststream())


if __name__ == "__main__":
    asyncio.run(main())
