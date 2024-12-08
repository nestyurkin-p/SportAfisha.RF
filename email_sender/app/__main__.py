import logging
import asyncio

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)


from .stream import faststream_runner


async def main():
    await asyncio.gather(faststream_runner())


if __name__ == "__main__":
    asyncio.run(main())
