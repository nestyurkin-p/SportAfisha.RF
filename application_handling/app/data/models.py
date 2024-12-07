from pydantic import BaseModel
from uuid import UUID
from typing import Dict, Optional


class CreateApplicationRequest(BaseModel):
    token: str
    event_id: UUID
    creator_id: UUID
    application_type: str
    results: Optional[Dict] = None


class ProcessApplicationRequest(BaseModel):
    token: str
    application_id: UUID
    approved: bool
