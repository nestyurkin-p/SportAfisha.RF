import os
import logging
import sqlalchemy

from sqlalchemy.orm import Session

from .models import *
from .database import get_db
from .memcache import memcache
from .oauth.token import get_user_password_hash


class CRUDException(Exception):
    pass


class UserNotExistsError(CRUDException):
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
        create_user(
            email,
            password,
            Role.superuser,
            owner_id=None,
            email_verified=True,
            db=next(get_db()),
        )
        logging.info("Superuser was created successfully")
    except UserExistsError:
        logging.info("Superuser exists already - skipping creation")


def create_user(
    email: str,
    password: str,
    role: Role,
    owner_id: uuid.UUID | None,
    email_verified: bool | None,
    db: Session,
) -> User:
    try:
        user = User(
            role=role,
            email=email,
            password_hash=get_user_password_hash(password),
            owner_id=owner_id,
            email_verified=email_verified,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except sqlalchemy.exc.IntegrityError:
        raise UserExistsError


class TokenNotExistsError(CRUDException):
    pass


class TokenMismatchError(CRUDException):
    pass


def verify_email(email: str, token: str, db: Session):
    user = db.query(User).filter_by(email=email).first()
    valid_token = memcache.get_email_token(email)

    if valid_token is None:
        raise TokenNotExistsError

    if valid_token == token:
        user.email_verified = True
        memcache.erase_email_token(email)
    else:
        raise TokenMismatchError

    db.commit()
    db.refresh(user)


def check_email_verification(user_id: uuid.UUID) -> bool:
    db = next(get_db())
    user = db.get(User, user_id)
    if user is None:
        raise UserNotExistsError
    return user.verified


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
