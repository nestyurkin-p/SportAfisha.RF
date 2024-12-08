from sqlalchemy import Column, String, Date, UUID
import uuid
from database import Base


class Office(Base):
    __tablename__ = "offices"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    federal_district = Column(String)
    region = Column(String)
    email = Column(String, index=True)
    director_name = Column(String, index=True)
