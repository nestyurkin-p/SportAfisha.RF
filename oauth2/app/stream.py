import logging

from enum import Enum
from pydantic import BaseModel
from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitQueue

from .oauth.exceptions import CredentialsValidationError


from .models import Role
from .memcache import memcache
from .oauth.token import get_token_data

broker = RabbitBroker("amqp://root:toor@rabbitmq:5672/")
app = FastStream(broker)

VALIDATE_REQQ = "oauth-validate-request-queue"
VALIDATE_RESPQ = "oauth-validate-response-queue"
REGISTER_REQQ = "oauth-register-request-queue"
REGISTER_RESPQ = "oauth-register-response-queue"

QUEUES = [VALIDATE_REQQ, VALIDATE_RESPQ, REGISTER_REQQ, REGISTER_RESPQ]


class ValidationRequest(BaseModel):
    token: str


class ValidationResponse(BaseModel):
    token: str
    validated: bool
    role: Role | None = None


class RegisterRequest(BaseModel):
    email: str
    require_email_verification: bool
    password: str


class VerificationStatus(str, Enum):
    pending = "pending_verification"
    verified = "verified"


class RegisterResponse(BaseModel):
    email: str
    email_status: VerificationStatus


@app.after_startup
async def startup():
    for queue in QUEUES:
        await broker.declare_queue(RabbitQueue(queue))


@broker.subscriber(VALIDATE_REQQ)
@broker.publisher(VALIDATE_RESPQ)
async def request_handler(message: ValidationRequest):
    try:
        raw_token = message.token
        token_data = get_token_data(raw_token)
        validated = memcache.check_jwt(raw_token)
        return ValidationResponse(
            token=raw_token,
            role=token_data.user_role,
            validated=validated,
        )
    except CredentialsValidationError:
        return ValidationResponse(
            token=raw_token,
            validated=False,
        )


async def faststream_runner():
    await app.run()
