# Add this line to the endpoint function in addition to (token: str) parameter:
#
# await oauth.validate(token, [oauth.Role.superuser])

import os
import enum
import asyncio

from fastapi import Depends, HTTPException, status
from pydantic import BaseModel
from typing import Annotated, Collection
from fastapi.security import OAuth2PasswordBearer

from broker import broker

DISABLE_VALIDATION = bool(int(os.getenv("DEBUG", "0")))

validation_map = {}

VALIDATE_REQQ = "oauth-validate-request-queue"
VALIDATE_RESPQ = "oauth-validate-response-queue"
REGISTER_REQQ = "oauth-register-request-queue"
REGISTER_RESPQ = "oauth-register-response-queue"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="")


def token(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    return token


class Role(str, enum.Enum):
    superuser = "superuser"
    office = "office"
    athlete = "athlete"


class ValidationRequest(BaseModel):
    token: str


class ValidationResponse(BaseModel):
    token: str
    validated: bool
    role: Role | None = None


async def publish_credentials(token):
    await broker.publish(ValidationRequest(token=token), VALIDATE_REQQ)


@broker.subscriber(VALIDATE_RESPQ)
async def validation_catcher(response: ValidationResponse):
    validation_map[response.token] = response


async def get_validation(token) -> ValidationResponse:
    validation_map[token] = None
    while True:
        if (response := validation_map.pop(token, None)) is not None:
            break
        await asyncio.sleep(0.05)
    return response


async def _validate(token: str, roles: Collection[Role | str] | None) -> bool:
    if DISABLE_VALIDATION:
        return True
    await publish_credentials(token)
    response = await get_validation(token)
    if response.validated and (response.role in roles or roles is None):
        return True
    return False


async def validate(token: str, roles: Collection[Role | str] | None):
    if not await _validate(token, roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
