from fastapi import Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer

from ..models import User
from ..database import get_db
from ..memcache import memcache

from .token import *
from .exceptions import *

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="sessions")


def get_token(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    if not memcache.check_jwt(token):
        raise SessionValidationError
    return token


def get_current_user(
    token: Annotated[str, Depends(get_token)],
    db: Session = Depends(get_db),
) -> User:
    token_data = get_token_data(token)

    user = db.query(models.User).get(token_data.user_id)

    if user is None:
        raise CredentialsValidationError

    return user
