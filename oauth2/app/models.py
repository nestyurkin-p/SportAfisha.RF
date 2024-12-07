import uuid
import enum

from sqlalchemy import UUID, Column, String, Enum
from .database import SqlAlchemyBase


class Role(enum.StrEnum):
    SUPERUSER = "superuser"
    OFFICE = "office"
    ATHLETE = "athlete"


class User(SqlAlchemyBase):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role = Column(Enum(Role))
    email = Column(String, unique=True)
    password_hash = Column(String)
    owner_id = Column(UUID(as_uuid=True), nullable=True)
