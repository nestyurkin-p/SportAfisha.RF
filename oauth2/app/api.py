import uvicorn

from typing import Any
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter, Depends, HTTPException, status

from .models import Role
from .database import get_db
from . import oauth, models, crud
from .oauth import get_current_user
from .oauth.routers import close_session
from .oauth.dependencies import get_token


class UserIn(BaseModel):
    email: str | None = None
    password: str | None = None
    role: Role | None = None


class UserOut(BaseModel):
    id: int
    email: str
    role: Role

    class Config:
        from_attributes = True


healthcheck_router = APIRouter()


@healthcheck_router.get("/healthcheck")
def healthcheck() -> Any:
    return {"status": "ok"}


user_router = APIRouter()


@user_router.post("/users", response_model=UserOut, tags=["User methods"])
def register_new_user(user: UserIn, db: Session = Depends(get_db)) -> Any:
    if user.email is None or user.password is None:
        raise HTTPException(
            status.HTTP_406_NOT_ACCEPTABLE,
            detail="New user's email or password was not provided",
        )
    try:
        return crud.create_user(**user.model_dump(), db=db)
    except crud.UserExistsError:
        raise HTTPException(
            status.HTTP_406_NOT_ACCEPTABLE,
            detail="User with such email already exists",
        )


@user_router.get("/users", response_model=UserOut, tags=["User methods"])
def current_user(
    user: models.User = Depends(get_current_user),
) -> Any:
    return user


@user_router.put(
    "/users", status_code=status.HTTP_204_NO_CONTENT, tags=["User methods"]
)
def edit_user(
    new_user: UserIn,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        crud.update_user(**new_user.model_dump(), user=current_user, db=db)
    except crud.UserExistsError:
        raise HTTPException(
            status.HTTP_406_NOT_ACCEPTABLE,
            detail="User with such email already exists",
        )


@user_router.delete(
    "/users", status_code=status.HTTP_204_NO_CONTENT, tags=["User methods"]
)
def remove_user(
    user: models.User = Depends(get_current_user),
    token: str = Depends(get_token),
    db: Session = Depends(get_db),
):
    crud.delete_user(user, db)
    close_session(token)


def fastapi_app():
    app = FastAPI()

    app.include_router(healthcheck_router)
    app.include_router(oauth.router)
    app.include_router(user_router)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


async def fastapi_runner():
    await uvicorn.Server(
        uvicorn.Config(
            fastapi_app(),
            host="0.0.0.0",
            port=80,
        ),
    ).serve()
