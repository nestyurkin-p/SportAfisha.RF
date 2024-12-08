import uuid
import enum

from sqlalchemy import UUID, Column, String, Enum, Boolean
from .database import SqlAlchemyBase


class Role(str, enum.Enum):
    superuser = "superuser"
    office = "office"
    athlete = "athlete"


class User(SqlAlchemyBase):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role = Column(Enum(Role))
    email = Column(String, unique=True)
    email_verified = Column(Boolean, default=False)
    password_hash = Column(String)
    owner_id = Column(UUID(as_uuid=True), nullable=True)
