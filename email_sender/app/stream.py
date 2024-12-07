import logging

from . import mail
from pydantic import BaseModel
from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitQueue

broker = RabbitBroker("amqp://root:toor@rabbitmq:5672/")
app = FastStream(broker)

REQQ = "email-request-queue"
RESPQ = "email-response-queue"

QUEUES = [REQQ, RESPQ]


class Request(BaseModel):
    address: str
    content: str


class Response(Request):
    status: str


@app.after_startup
async def startup():
    for queue in QUEUES:
        await broker.declare_queue(RabbitQueue(queue))


@broker.subscriber(REQQ)
@broker.publisher(RESPQ)
async def request_handler(message: Request):
    mail.send(receiver_email=message.address, message=message.content)


async def faststream_runner():
    await app.run()
