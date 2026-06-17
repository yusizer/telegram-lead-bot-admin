"""Entrypoint: run the Telegram bot (polling) and the FastAPI admin together."""
import asyncio
import os

import uvicorn

from .bot import start_bot
from .config import settings
from .database import init_db
from .web import app


async def main() -> None:
    await init_db()

    port = int(os.environ.get("PORT", settings.web_port))
    config = uvicorn.Config(
        app, host=settings.web_host, port=port, log_level="info"
    )
    server = uvicorn.Server(config)

    # Both tasks share one event loop.
    await asyncio.gather(start_bot(), server.serve())


if __name__ == "__main__":
    asyncio.run(main())
