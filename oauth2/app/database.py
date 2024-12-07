import os
import sqlalchemy as sa

from sqlalchemy.orm import Session, declarative_base, sessionmaker


def get_db_url():
    POSTGRES_HOST_FALLBACK = "localhost"
    POSTGRES_USER_FALLBACK = "root"
    POSTGRES_PASSWORD_FALLBACK = "toor"
    POSTGRES_DATABASE_FALLBACK = "credentials"

    POSTGRES_USER = os.getenv("POSTGRES_USER", POSTGRES_USER_FALLBACK)
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", POSTGRES_HOST_FALLBACK)
    POSTGRES_DATABASE = os.getenv("POSTGRES_DB", POSTGRES_DATABASE_FALLBACK)
    POSTGRES_PASSWORD_FILE = os.getenv("POSTGRES_PASSWORD_FILE")

    def get_postgres_password():
        if POSTGRES_PASSWORD_FILE:
            with open(POSTGRES_PASSWORD_FILE) as file:
                return file.read().rstrip()
        return POSTGRES_PASSWORD_FALLBACK

    return f"postgresql+psycopg2://{POSTGRES_USER}:{get_postgres_password()}@{POSTGRES_HOST}:5432/{POSTGRES_DATABASE}"


engine = sa.create_engine(get_db_url(), echo=False)
engine.update_execution_options(connect_args={"connect_timeout": 5})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

SqlAlchemyBase = declarative_base()


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
