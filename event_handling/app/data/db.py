from contextlib import AbstractContextManager
import sqlalchemy as sa
import os
import logging

import sqlalchemy.ext.declarative as dec
import sqlalchemy.orm as orm


SqlAlchemyBase = dec.declarative_base()


factory = None
engine = None


POSTGRES_HOST_FALLBACK = "event_db"
POSTGRES_USER_FALLBACK = "postgres"
POSTGRES_PASSWORD_FALLBACK = "toor"
POSTGRES_DATABASE_FALLBACK = "event_db"
POSTGRES_PORT_FALLBACK = 5434

POSTGRES_USER = os.getenv("EVENT_DB_POSTGRES_USER", POSTGRES_USER_FALLBACK)
POSTGRES_PORT = os.getenv("EVENT_DB_POSTGRES_PORT", POSTGRES_PORT_FALLBACK)
POSTGRES_HOST = os.getenv("EVENT_DB_POSTGRES_HOST", POSTGRES_HOST_FALLBACK)
POSTGRES_DATABASE = os.getenv("EVENT_DB_POSTGRES_DB", POSTGRES_DATABASE_FALLBACK)
POSTGRES_PASSWORD_FILE = os.getenv("EVENT_DB_POSTGRES_PASSWORD_FILE")

def get_db_url(i_am_alembic: bool = False):
    def get_postgres_password():
        if POSTGRES_PASSWORD_FILE:
            with open(POSTGRES_PASSWORD_FILE) as file:
                return file.read().rstrip()
        return POSTGRES_PASSWORD_FALLBACK

    if i_am_alembic:
        return f"postgresql+psycopg2://{POSTGRES_USER}:{get_postgres_password()}@0.0.0.0:{POSTGRES_PORT}/{POSTGRES_DATABASE}"

    return f"postgresql+psycopg2://{POSTGRES_USER}:{get_postgres_password()}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"


def global_init():
    global factory
    global engine

    if factory:
        return

    logging.info(f"postgres_db_url: {get_db_url()}")
    engine = sa.create_engine(get_db_url(), echo=False)
    engine.update_execution_options(connect_args={"connect_timeout": 5})
    factory = orm.sessionmaker(bind=engine)

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)

    logging.info("Postgres database connection was initialized successfully")


def remove():
    global factory
    if factory:
        factory.close_all()


def make_thread_safe():
    if engine:
        engine.dispose()
    remove()


class session(AbstractContextManager):
    def __init__(self):
        global factory
        if isinstance(factory, orm.sessionmaker):
            self.session = factory()
        else:
            logging.error("Factory not filling")
            exit(1)

    def __enter__(self):
        return self.session

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self.session.rollback()
        self.session.close()

