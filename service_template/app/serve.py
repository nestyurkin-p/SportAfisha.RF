import logging

from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitQueue

logging.basicConfig()

broker = RabbitBroker("amqp://root:toor@rabbitmq:5672/")
app = FastStream(broker)


@app.after_startup
async def startup():
    await broker.declare_queue(RabbitQueue("test-queue"))
    await broker.publish("Hello World!", queue="test-queue")


@broker.subscriber("test-queue")
async def base_handler(body):
    logging.info(f"Got message: {body}")
