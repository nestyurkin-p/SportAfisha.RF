import logging
import asyncio

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
from .database import engine
from .models import SqlAlchemyBase

SqlAlchemyBase.metadata.create_all(engine)

from .api import fastapi_runner
from .crud import create_superuser
from .stream import faststream_runner


async def main():
    await asyncio.gather(
        create_superuser(),
        fastapi_runner(),
        faststream_runner(),
    )


if __name__ == "__main__":
    asyncio.run(main())
