import asyncio
import logging
import os
import json
from datetime import date
from typing import List, Dict

import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitQueue, message
from sqlalchemy.orm import Session
from uuid import UUID

from database import Base, engine, SessionLocal, get_db
from models import Athlete
from schemas import AthleteCreate, AthleteUpdate, AthleteInDB, StatusResponse

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api = FastAPI()

# Получение URL для подключения к RabbitMQ из переменных окружения
RABBIT_URL = os.getenv("RABBIT_URL", "amqp://root:toor@rabbitmq:5672/")
broker = RabbitBroker(RABBIT_URL)

# Инициализация FastStream
app = FastStream(broker)

# Создание таблиц в базе данных при запуске приложения
Base.metadata.create_all(bind=engine)

# Эндпоинт для проверки работоспособности API
@api.get("/")
async def read_root():
    return {"message": "Hello from FastAPI"}

# Эндпоинт для создания спортсмена
@api.post("/create_athlete", response_model=StatusResponse)
async def create_athlete(athlete: AthleteCreate, db: Session = Depends(get_db)):
    logger.info(f"[CREATE] Attempting to create athlete with UIN: {athlete.UIN}")

    # Создание нового спортсмена
    new_athlete = Athlete(**athlete.model_dump())
    db.add(new_athlete)
    db.commit()
    db.refresh(new_athlete)

    logger.info(f"[CREATE] Athlete created with ID: {new_athlete.id}, UIN: {new_athlete.UIN}")

    # Отправка сообщения в очередь RabbitMQ
    await broker.publish({"action": "created", "athlete_id": str(new_athlete.id)}, queue="athlete_events")

    # Возвращаем статус и id
    return {"status": "OK", "id": new_athlete.id}

# Эндпоинт для обновления спортсмена по ID
@api.post("/update_athlete", response_model=StatusResponse)
async def update_athlete(athlete: AthleteUpdate, db: Session = Depends(get_db)):
    logger.info(f"[UPDATE] Attempting to update athlete with ID: {athlete.id}")

    # Поиск спортсмена по ID
    db_athlete = db.query(Athlete).filter(Athlete.id == athlete.id).first()

    if not db_athlete:
        logger.warning(f"[UPDATE] Athlete with ID {athlete.id} not found.")
        raise HTTPException(status_code=404, detail="Athlete not found")

    # Обновление полей спортсмена, исключая ID
    update_data = athlete.model_dump()
    update_data.pop("id", None)

    for field, value in update_data.items():
        if value:  # Обновляем только непустые поля
            setattr(db_athlete, field, value)

    db.commit()
    db.refresh(db_athlete)

    logger.info(f"[UPDATE] Athlete with ID: {db_athlete.id} (UIN: {db_athlete.UIN}) has been updated.")

    # Отправка сообщения в очередь RabbitMQ
    await broker.publish({"action": "updated", "athlete_id": str(db_athlete.id)}, queue="athlete_events")

    # Возвращаем статус и id
    return {"status": "OK", "id": db_athlete.id}

# Эндпоинт для получения всех спортсменов с пагинацией
@api.get("/athletes", response_model=List[AthleteInDB])
async def get_athletes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Возвращает список спортсменов с возможностью пагинации.
    """
    athletes = db.query(Athlete).offset(skip).limit(limit).all()
    logger.info(f"[GET] Retrieved {len(athletes)} athletes from the database.")
    return athletes

# Эндпоинт для получения конкретного спортсмена по ID
@api.get("/athletes/{athlete_id}", response_model=AthleteInDB)
async def get_athlete(athlete_id: UUID, db: Session = Depends(get_db)):
    """
    Возвращает информацию о конкретном спортсмене по его ID.
    """
    athlete = db.query(Athlete).filter(Athlete.id == athlete_id).first()
    if not athlete:
        logger.warning(f"[GET] Athlete with ID {athlete_id} not found.")
        raise HTTPException(status_code=404, detail="Athlete not found")
    logger.info(f"[GET] Retrieved athlete with ID {athlete_id}.")
    return athlete

# Настройка FastStream для работы с RabbitMQ
@app.after_startup
async def startup():
    # Объявление очередей
    await broker.declare_queue(RabbitQueue("test-queue"))
    await broker.declare_queue(RabbitQueue("athlete_events"))
    await broker.declare_queue(RabbitQueue("create_athlete"))
    await broker.declare_queue(RabbitQueue("update_athlete"))
    await broker.declare_queue(RabbitQueue("responses"))

    # Отправка тестового сообщения
    await broker.publish("Hello World!", queue="test-queue")

# Подписчик на очередь test-queue
@broker.subscriber("test-queue")
async def base_handler(body):
    logger.info(f"Got message from test-queue: {body}")

# Подписчик на очередь athlete_events
@broker.subscriber("athlete_events")
async def athlete_event_handler(body):
    logger.info(f"Got athlete event: {body}")

# Подписчик на очередь create_athlete
@broker.subscriber("create_athlete")
async def create_athlete_request_handler(message: message):
    """
    Обработчик сообщений из очереди create_athlete.
    Ожидает сообщение с параметрами для создания спортсмена.
    Отправляет ответ 'OK' и 'id' обратно в reply_to очередь.
    """
    try:
        data = json.loads(message.body)
        logger.info(f"[MQ CREATE] Received message: {data}")

        # Извлечение reply_to и correlation_id
        reply_to = message.properties.reply_to
        correlation_id = message.properties.correlation_id

        if not reply_to or not correlation_id:
            logger.error("[MQ CREATE] Missing reply_to or correlation_id in message properties.")
            return

        # Создание объекта AthleteCreate
        athlete_create = AthleteCreate(
            id=data["id"],  # Ожидаем, что id передан как UUID
            name=data["name"],
            location=data["location"],
            email=data["email"],
            UIN=data["UIN"],
            birth_date=date.fromisoformat(data["birth_date"]),
            phone_number=data["phone_number"]
        )

        # Создание спортсмена
        db = SessionLocal()
        try:
            new_athlete = Athlete(**athlete_create.model_dump())
            db.add(new_athlete)
            db.commit()
            db.refresh(new_athlete)
            logger.info(f"[MQ CREATE] Athlete created with ID: {new_athlete.id}, UIN: {new_athlete.UIN}")
            response = {"status": "OK", "id": str(new_athlete.id)}
        except Exception as e:
            logger.error(f"[MQ CREATE] Error creating athlete: {e}")
            response = {"status": "error", "message": "Internal server error"}
        finally:
            db.close()

        # Отправка ответа
        await broker.publish(json.dumps(response), queue=reply_to, correlation_id=correlation_id)
        logger.info(f"[MQ CREATE] Sent response to {reply_to} with correlation_id {correlation_id}")

    except json.JSONDecodeError:
        logger.error("[MQ CREATE] Failed to decode JSON from message body.")
    except KeyError as e:
        logger.error(f"[MQ CREATE] Missing key in message data: {e}")

# Подписчик на очередь update_athlete
@broker.subscriber("update_athlete")
async def update_athlete_request_handler(message: message):
    """
    Обработчик сообщений из очереди update_athlete.
    Ожидает сообщение с параметрами для обновления спортсмена по ID.
    Отправляет ответ 'OK' обратно в reply_to очередь.
    """
    try:
        data = json.loads(message.body)
        logger.info(f"[MQ UPDATE] Received message: {data}")

        # Извлечение reply_to и correlation_id
        reply_to = message.properties.reply_to
        correlation_id = message.properties.correlation_id

        if not reply_to or not correlation_id:
            logger.error("[MQ UPDATE] Missing reply_to or correlation_id in message properties.")
            return

        # Проверка наличия ID
        athlete_id = data.get("id")
        if not athlete_id:
            logger.error("[MQ UPDATE] Missing 'id' in message data.")
            response = {"status": "error", "message": "Missing 'id' in message data"}
            await broker.publish(json.dumps(response), queue=reply_to, correlation_id=correlation_id)
            return

        # Проверка валидности UUID
        try:
            athlete_uuid = UUID(str(athlete_id))
        except ValueError:
            logger.error("[MQ UPDATE] Invalid UUID format for id.")
            response = {"status": "error", "message": "Invalid UUID format for id"}
            await broker.publish(json.dumps(response), queue=reply_to, correlation_id=correlation_id)
            return

        # Создание объекта AthleteUpdate
        athlete_update = AthleteUpdate(
            id=athlete_uuid,
            name=data.get("name", ""),
            location=data.get("location", ""),
            email=data.get("email", ""),
            UIN=data.get("UIN", ""),
            birth_date=date.fromisoformat(data["birth_date"]) if data.get("birth_date") else date.today(),
            phone_number=data.get("phone_number", "")
        )

        # Обновление спортсмена
        db = SessionLocal()
        try:
            db_athlete = db.query(Athlete).filter(Athlete.id == athlete_update.id).first()
            if not db_athlete:
                logger.warning(f"[MQ UPDATE] Athlete with ID {athlete_update.id} not found.")
                response = {"status": "error", "message": "Athlete not found"}
            else:
                update_data = athlete_update.model_dump()
                update_data.pop("id", None)  # Удаляем id из обновляемых данных
                for field, value in update_data.items():
                    if value:  # Обновляем только непустые поля
                        setattr(db_athlete, field, value)
                db.commit()
                db.refresh(db_athlete)
                logger.info(f"[MQ UPDATE] Athlete with ID: {db_athlete.id} (UIN: {db_athlete.UIN}) has been updated.")
                response = {"status": "OK", "id": str(db_athlete.id)}
        except Exception as e:
            logger.error(f"[MQ UPDATE] Error updating athlete: {e}")
            response = {"status": "error", "message": "Internal server error"}
        finally:
            db.close()

        # Отправка ответа
        await broker.publish(json.dumps(response), queue=reply_to, correlation_id=correlation_id)
        logger.info(f"[MQ UPDATE] Sent response to {reply_to} with correlation_id {correlation_id}")

    except json.JSONDecodeError:
        logger.error("[MQ UPDATE] Failed to decode JSON from message body.")
    except KeyError as e:
        logger.error(f"[MQ UPDATE] Missing key in message data: {e}")

# Подписчик на очередь responses
@broker.subscriber("responses")
async def responses_handler(body, message: message):
    """
    Обработчик сообщений из очереди responses.
    Используется для получения ответов на запросы через RabbitMQ.
    """
    try:
        response = json.loads(body)
        correlation_id = message.properties.correlation_id
        logger.info(f"[RESPONSES] Received response for correlation_id {correlation_id}: {response}")
    except json.JSONDecodeError:
        logger.error("[RESPONSES] Failed to decode JSON from message body.")
    except KeyError as e:
        logger.error(f"[RESPONSES] Missing key in message data: {e}")

# Функция для запуска FastStream
async def start_faststream():
    await app.run()

# Функция для запуска FastAPI с помощью Uvicorn
async def start_fastapi():
    config = uvicorn.Config(api, host="0.0.0.0", port=8003, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

# Главная функция для запуска обоих приложений одновременно
async def main():
    await asyncio.gather(
        start_fastapi(),
        start_faststream()
    )

if __name__ == "__main__":
    asyncio.run(main())
