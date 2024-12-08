import os
import uuid
import logging

from enum import Enum
from uuid import UUID
from pydantic import BaseModel
from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitQueue

from . import crud
from .models import Role
from .database import get_db
from .memcache import memcache
from .oauth.token import get_token_data
from .oauth.exceptions import CredentialsValidationError

broker = RabbitBroker("amqp://root:toor@rabbitmq:5672/")
app = FastStream(broker)

VALIDATE_REQQ = "oauth-validate-request-queue"
VALIDATE_RESPQ = "oauth-validate-response-queue"
REGISTER_REQQ = "oauth-register-request-queue"
REGISTER_RESPQ = "oauth-register-response-queue"

QUEUES = [VALIDATE_REQQ, VALIDATE_RESPQ, REGISTER_REQQ, REGISTER_RESPQ]

DOMAIN = os.getenv("DOMAIN", "localhost")


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
    role: Role
    owner_id: UUID


class RegisterStatus(str, Enum):
    pending = "pending"
    verified = "verified"
    already_exists = "already_exists"


class RegisterResponse(BaseModel):
    email: str
    status: RegisterStatus


class EmailRequest(BaseModel):
    address: str
    content: str


@app.after_startup
async def startup():
    for queue in QUEUES:
        await broker.declare_queue(RabbitQueue(queue))


@broker.subscriber(VALIDATE_REQQ)
@broker.publisher(VALIDATE_RESPQ)
async def validation_handler(message: ValidationRequest):
    logging.info("Got {message}")
    try:
        raw_token = message.token
        token_data = get_token_data(raw_token)
        validated = memcache.check_jwt(raw_token)
        crud.check_email_verification(UUID(token_data.user_id))
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


@broker.subscriber(REGISTER_REQQ)
@broker.publisher(REGISTER_RESPQ)
async def registration_handler(message: RegisterRequest):
    logging.info("Got {message}")

    db = next(get_db())
    email = message.email

    try:
        crud.create_user(
            email=email,
            password=message.password,
            owner_id=message.owner_id,
            role=message.role,
            email_verified=not message.require_email_verification,
            db=db,
        )
    except crud.UserExistsError:
        return RegisterResponse(email=email, status=RegisterStatus.already_exists)

    if not message.require_email_verification:
        return RegisterResponse(email=email, status=RegisterStatus.verified)

    if memcache.check_email_token(email):
        return RegisterResponse(email=email, status=RegisterStatus.pending)

    memcache.register_email_token(email, token=str(uuid.uuid4()))

    token = memcache.get_email_token(email)

    confurl = f"http://{DOMAIN}/verify?token={token}"
    content = f"Ссылка для подтверждения почты: {confurl}"

    await broker.publish(
        EmailRequest(address=email, content=content), "email-request-queue"
    )

    return RegisterResponse(email=email, status=RegisterStatus.pending)


async def faststream_runner():
    await app.run()
