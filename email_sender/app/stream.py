import logging

from pydantic import BaseModel
from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitQueue

from .mail import postbox_send

broker = RabbitBroker("amqp://root:toor@rabbitmq:5672/")
app = FastStream(broker)

REQQ = "email-request-queue"
RESPQ = "email-response-queue"

QUEUES = [REQQ, RESPQ]


class Request(BaseModel):
    address: str
    topic: str
    content: str


class Response(Request):
    status: str


@app.after_startup
async def startup():
    for queue in QUEUES:
        await broker.declare_queue(RabbitQueue(queue))
    print("Made brokers")
    postbox_send("markmelix@gmail.com", "test mail topic", "test mail content")
    print("sent message")


@broker.subscriber(REQQ)
@broker.publisher(RESPQ)
async def request_handler(message: Request):
    pass


async def faststream_runner():
    await app.run()
