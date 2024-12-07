from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import os

DATABASE_URL = "postgresql://postgres:toor@application_db:5433/application_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_applications_table():
    try:
        Base.metadata.create_all(bind=engine)
        print("Таблица `applications` успешно создана.")
    except Exception as e:
        print(f"Ошибка при создании таблицы `applications`: {e}")
