from sqlalchemy import Column, String, Date, UUID
import uuid
from database import Base


class Athlete(Base):
    __tablename__ = "athletes"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = Column(String, index=True)
    location = Column(String)
    email = Column(String, index=True)
    UIN = Column(String, index=True)
    birth_date = Column(Date)
    phone_number = Column(String)
