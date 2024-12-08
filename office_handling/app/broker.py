import os

from faststream.rabbit import RabbitBroker

RABBIT_URL = os.getenv("RABBIT_URL", "amqp://root:toor@rabbitmq:5672/")
broker = RabbitBroker(RABBIT_URL)
