import sqlalchemy as sa
from app.data.db import SqlAlchemyBase


class Event(SqlAlchemyBase):
    __tablename__ = "events"
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    title = sa.Column(sa.String)
    age_group = sa.Column(sa.String)
    female = sa.Column(sa.Boolean)
    male = sa.Column(sa.Boolean)
    is_approved = sa.Column(sa.Boolean)
    discipline = sa.Column(sa.String)
    results = sa.Column(sa.String, nullable=True)
    date_start = sa.Column(sa.Date)
    date_finished = sa.Column(sa.Date)
    location = sa.Column(sa.String)
    description = sa.Column(sa.String)
