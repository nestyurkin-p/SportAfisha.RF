import os
import jwt

from pydantic import BaseModel
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

from .. import models
from .exceptions import *


def get_secret_key():
    SECRET_KEY_FILE = os.getenv("JWT_SECRET_KEY_FILE", "/run/secrets/jwt_secret_key")
    try:
        with open(SECRET_KEY_FILE) as file:
            return file.read().rstrip()
    except FileNotFoundError:
        raise JWTSecretKeyNotFoundError(SECRET_KEY_FILE)


SECRET_KEY = get_secret_key()
JWT_ALGORITHM = "HS256"
PWD_ALGORITHM = "bcrypt"

pwd_context = CryptContext(schemes=[PWD_ALGORITHM], deprecated="auto")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: str
    user_role: models.Role


def get_user_password_hash(password):
    return pwd_context.hash(password)


def verify_user_password(plain_password, password_hash):
    return pwd_context.verify(plain_password, password_hash)


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(models.User).filter_by(email=username).first()
    if not user:
        return False
    if not verify_user_password(password, user.password_hash):
        return False
    return user


def create_user_access_token(
    user_id: str, user_role: models.Role, expires_delta: timedelta
) -> Token:
    expire = datetime.now(timezone.utc) + expires_delta
    data = {
        "sub": user_id,
        "exp": expire,
        "roles": [user_role],
    }
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return Token(access_token=encoded_jwt, token_type="bearer")


def get_token_data(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        roles = payload.get("roles")

        if user_id is None or roles is None or len(roles) == 0:
            raise CredentialsValidationError

        return TokenData(user_id=user_id, user_role=roles[0])

    # Signature expiration error gets handled either
    except jwt.InvalidTokenError:
        raise CredentialsValidationError
