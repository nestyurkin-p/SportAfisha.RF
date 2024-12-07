import uuid
import sqlalchemy as sa
from app.data.db import SqlAlchemyBase


class Event(SqlAlchemyBase):
    __tablename__ = "events"
    id = sa.Column(sa.UUID, primary_key=True, default=uuid.uuid4)
    title = sa.Column(sa.String)
    age_group = sa.Column(sa.String)
    females = sa.Column(sa.Boolean)
    males = sa.Column(sa.Boolean)
    is_approved = sa.Column(sa.Boolean, nullable=True, default=None)
    discipline = sa.Column(sa.String)
    results = sa.Column(sa.JSON, nullable=True)
    date_start = sa.Column(sa.Date)
    date_finished = sa.Column(sa.Date)
    location = sa.Column(sa.String)
    description = sa.Column(sa.TEXT)
    is_local = sa.Column(sa.Boolean)

