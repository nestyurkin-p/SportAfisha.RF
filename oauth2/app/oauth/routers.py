from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ..database import get_db
from ..memcache import memcache

from .dependencies import *

router = APIRouter()

ACCESS_TOKEN_EXPIRES = timedelta(days=60)


def create_session(raw_jwt: str):
    memcache.register_jwt(raw_jwt)


def close_session(raw_jwt: str):
    memcache.erase_jwt(raw_jwt)


@router.post("/sessions", tags=["OAuth2 methods"])
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_user_access_token(str(user.id), user.role, ACCESS_TOKEN_EXPIRES)
    background_tasks.add_task(create_session, token.access_token)
    return token


@router.delete(
    "/sessions", status_code=status.HTTP_204_NO_CONTENT, tags=["OAuth2 methods"]
)
def logout(token: str = Depends(get_token)):
    close_session(token)
