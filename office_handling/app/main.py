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
from models import Office
from schemas import OfficeCreate, OfficeUpdate, OfficeInDB, StatusResponse

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

# Эндпоинт для создания региона
@api.post("/create_office", response_model=StatusResponse)
async def create_office(office: OfficeCreate, db: Session = Depends(get_db)):
    # Создание нового office
    new_office = Office(**office.model_dump())
    db.add(new_office)
    db.commit()
    db.refresh(new_office)

    # Отправка сообщения в очередь RabbitMQ
    await broker.publish({"action": "created", "office_id": str(new_office.id)}, queue="office_events")

    # Возвращаем статус и id
    return {"status": "OK", "id": office.id}

# Эндпоинт для обновления office по ID
@api.post("/update_office", response_model=StatusResponse)
async def update_office(office: OfficeUpdate, db: Session = Depends(get_db)):
    logger.info(f"[UPDATE] Attempting to update office with ID: {office.id}")

    # Поиск office по ID
    db_office = db.query(Office).filter(Office.id == office.id).first()

    if not db_office:
        logger.warning(f"[UPDATE] Office with ID {office.id} not found.")
        raise HTTPException(status_code=404, detail="Office not found")

    # Обновление полей office, исключая ID
    update_data = office.model_dump()
    update_data.pop("id", None)

    for field, value in update_data.items():
        if value:  # Обновляем только непустые поля
            setattr(db_office, field, value)

    db.commit()
    db.refresh(db_office)

    logger.info(f"[UPDATE] Office with ID: {db_office.id} has been updated.")

    # Отправка сообщения в очередь RabbitMQ
    await broker.publish({"action": "updated", "office_id": str(db_office.id)}, queue="office_events")

    # Возвращаем статус и id
    return {"status": "OK", "id": db_office.id}

# Эндпоинт для получения всех offices с пагинацией
@api.get("/offices", response_model=List[OfficeInDB])
async def get_offices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Возвращает список offices с возможностью пагинации.
    """
    offices = db.query(Office).offset(skip).limit(limit).all()
    logger.info(f"[GET] Retrieved {len(offices)} offices from the database.")
    return offices

# Эндпоинт для получения конкретного office по ID
@api.get("/offices/{office_id}", response_model=OfficeInDB)
async def get_office(office_id: UUID, db: Session = Depends(get_db)):
    """
    Возвращает информацию о конкретном office по его ID.
    """
    office = db.query(Office).filter(Office.id == office_id).first()
    if not office:
        logger.warning(f"[GET] Office with ID {office_id} not found.")
        raise HTTPException(status_code=404, detail="Office not found")
    logger.info(f"[GET] Retrieved athlete with ID {office_id}.")
    return office

# Настройка FastStream для работы с RabbitMQ
@app.after_startup
async def startup():
    # Объявление очередей
    await broker.declare_queue(RabbitQueue("test-queue"))
    await broker.declare_queue(RabbitQueue("office_events"))
    await broker.declare_queue(RabbitQueue("create_office"))
    await broker.declare_queue(RabbitQueue("update_office"))
    await broker.declare_queue(RabbitQueue("responses"))

    # Отправка тестового сообщения
    await broker.publish("Hello World!", queue="test-queue")

# Подписчик на очередь test-queue
@broker.subscriber("test-queue")
async def base_handler(body):
    logger.info(f"Got message from test-queue: {body}")

# Подписчик на очередь office_events
@broker.subscriber("office_events")
async def office_event_handler(body):
    logger.info(f"Got office event: {body}")

# Подписчик на очередь create_office
@broker.subscriber("create_office")
async def create_office_request_handler(message: message):
    """
    Обработчик сообщений из очереди create_office.
    Ожидает сообщение с параметрами для создания office.
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

        # Создание объекта OfficeCreate
        office_create = OfficeCreate(
            id=data["id"],  # Ожидаем, что id передан как UUID
            federal_district=data["federal_district"],
            region=data["region"],
            email=data["email"],
            director_name=data["director_name"],
        )

        # Создание office
        db = SessionLocal()
        try:
            new_office = Office(**office_create.model_dump())
            db.add(new_office)
            db.commit()
            db.refresh(new_office)
            logger.info(f"[MQ CREATE] Office created with ID: {new_office.id}")
            response = {"status": "OK", "id": str(new_office.id)}
        except Exception as e:
            logger.error(f"[MQ CREATE] Error creating office: {e}")
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

# Подписчик на очередь update_office
@broker.subscriber("update_office")
async def update_office_request_handler(message: message):
    """
    Обработчик сообщений из очереди update_office.
    Ожидает сообщение с параметрами для обновления office по ID.
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
        office_id = data.get("id")
        if not office_id:
            logger.error("[MQ UPDATE] Missing 'id' in message data.")
            response = {"status": "error", "message": "Missing 'id' in message data"}
            await broker.publish(json.dumps(response), queue=reply_to, correlation_id=correlation_id)
            return

        # Проверка валидности UUID
        try:
            office_uuid = UUID(str(office_id))
        except ValueError:
            logger.error("[MQ UPDATE] Invalid UUID format for id.")
            response = {"status": "error", "message": "Invalid UUID format for id"}
            await broker.publish(json.dumps(response), queue=reply_to, correlation_id=correlation_id)
            return

        # Создание объекта OfficeUpdate
        office_update = OfficeUpdate(
            id=office_uuid,
            federal_district=data.get("federal_district", ""),
            region=data.get("region", ""),
            email=data.get("email", ""),
            director_name=data.get("director_name", ""),
        )

        # Обновление office
        db = SessionLocal()
        try:
            db_office = db.query(Office).filter(Office.id == office_update.id).first()
            if not db_office:
                logger.warning(f"[MQ UPDATE] Office with ID {office_update.id} not found.")
                response = {"status": "error", "message": "Office not found"}
            else:
                update_data = office_update.model_dump()
                update_data.pop("id", None)  # Удаляем id из обновляемых данных
                for field, value in update_data.items():
                    if value:  # Обновляем только непустые поля
                        setattr(db_office, field, value)
                db.commit()
                db.refresh(db_office)
                logger.info(f"[MQ UPDATE] Office with ID: {db_office.id} has been updated.")
                response = {"status": "OK", "id": str(db_office.id)}
        except Exception as e:
            logger.error(f"[MQ UPDATE] Error updating office: {e}")
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
