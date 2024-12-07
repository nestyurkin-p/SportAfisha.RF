import logging

from pydantic import BaseModel
from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitQueue

broker = RabbitBroker("amqp://root:toor@rabbitmq:5672/")
app = FastStream(broker)

# Main queue name
Q = "oauth-queue"


class DataBasic(BaseModel):
    sender: str
    type: str
    token: str


@app.after_startup
async def startup():
    await broker.declare_queue(RabbitQueue(Q))
    await broker.publish(DataBasic(sender="oauth2", type="test", token="none"), Q)


@broker.subscriber(Q)
async def request_handler(data: DataBasic):
    logging.info(f"Body '{data}' is {type(data)}")


async def faststream_runner():
    await app.run()
