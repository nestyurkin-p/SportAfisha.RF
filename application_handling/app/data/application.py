from sqlalchemy import Column, String, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from .database import Base
import uuid


class Application(Base):
    def to_dict(self):
        return {
            "application_id": str(self.id),
            "event_id": str(self.event_id),
            "application_type": self.application_type,
            "approved_status": self.approved,
            "creator_id": str(self.creator),
            "result": self.result,
        }

    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    event_id = Column(UUID(as_uuid=True), nullable=False)
    application_type = Column(String, nullable=False)
    approved = Column(Boolean, nullable=False)
    creator = Column(UUID(as_uuid=True), nullable=False)
    result = Column(JSON, nullable=True)
