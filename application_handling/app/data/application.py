from sqlalchemy import Column, String, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from .database import Base
import uuid


class Application(Base):
    def to_dict(self):
        return {
            "application_id": str(self.id),
            "event_id": str(self.event_id),
            "application_status": {
                "pending": self.pending,
                "confirmed": self.confirmed,
                "rejected": self.rejected,
            },
            "creator_id": str(self.creator_id),
            "results": self.results,
            "purpose": self.purpose
        }

    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    event_id = Column(UUID(as_uuid=True), nullable=False)
    purpose = Column(String, nullable=False)

    # статусы заявки
    pending: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    rejected: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    confirmed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    creator_id = Column(UUID(as_uuid=True), nullable=False)
    results = Column(JSON, nullable=True)
