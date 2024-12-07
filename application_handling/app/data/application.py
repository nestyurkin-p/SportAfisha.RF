from sqlalchemy import Column, String, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from .database import Base
import uuid


class Application(Base):
    def to_dict(self):
        return {
            "application_id": str(self.application_id),
            "event_id": str(self.event_id),
            "application_status": {"pending": self.pending, "confirmed": self.confirmed, "rejected": self.rejected},
            "creator_id": str(self.creator_id),
            "results": self.results,
        }

    __tablename__ = "applications"

    application_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    event_id = Column(UUID(as_uuid=True), nullable=False)
    application_purpose = Column(String, nullable=False)

    # статусы заявки
    pending = Column(Boolean, nullable=False, default=True)
    confirmed = Column(Boolean, nullable=False, default=False)
    rejected = Column(Boolean, nullable=False, default=False)

    creator_id = Column(UUID(as_uuid=True), nullable=False)
    results = Column(JSON, nullable=True)
