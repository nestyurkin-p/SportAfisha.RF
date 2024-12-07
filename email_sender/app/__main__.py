import logging
import asyncio

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)


from .stream import faststream_runner
from .mail import postbox_send


async def main():
    await asyncio.gather(faststream_runner())


if __name__ == "__main__":
    postbox_send("markmelix@gmail.com", "test_topic", "test_message")
    # asyncio.run(main())
