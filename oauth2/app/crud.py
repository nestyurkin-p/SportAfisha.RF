import os
import logging
import sqlalchemy

from sqlalchemy.orm import Session

from .models import *
from .database import get_db
from .oauth.token import get_user_password_hash


class CRUDException(Exception):
    pass


class UserExistsError(CRUDException):
    pass


class SuperuserUnspecifiedCredentialsError(CRUDException):
    pass


async def create_superuser():
    try:
        email = os.getenv("SUPERUSER_EMAIL")
        password = os.getenv("SUPERUSER_PASSWORD")
        if email is None or password is None:
            raise SuperuserUnspecifiedCredentialsError(
                "please, provide initial superuser credentials in the .env file"
            )
        create_user(email, password, Role.superuser, owner_id=None, db=next(get_db()))
        logging.info("Superuser was created successfully")
    except UserExistsError:
        logging.info("Superuser exists already - skipping creation")


def create_user(
    email: str, password: str, role: Role, owner_id: uuid.UUID | None, db: Session
) -> User:
    try:
        user = User(
            role=role,
            email=email,
            password_hash=get_user_password_hash(password),
            owner_id=owner_id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except sqlalchemy.exc.IntegrityError:
        raise UserExistsError


def update_user(
    email: str | None, password: str | None, role: Role | None, user: User, db: Session
):
    try:
        if email is not None:
            user.email = email
        if password is not None:
            user.password_hash = get_user_password_hash(password)
        if role is not None:
            user.role = role
        db.commit()
        db.refresh(user)
    except sqlalchemy.exc.IntegrityError:
        raise UserExistsError


def delete_user(user: User, db: Session):
    db.delete(user)
    db.commit()
