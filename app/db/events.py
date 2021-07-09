from fastapi import FastAPI
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import MONGO_DATABASE, MONGO_URI


async def connect_to_db(app: FastAPI) -> None:
    logger.info("Connecting to {0}", repr(MONGO_URI))
    app.state.db_client = AsyncIOMotorClient(MONGO_URI)
    app.state.db = app.state.db_client[MONGO_DATABASE]
    logger.info("Connection established")


async def close_db_connection(app: FastAPI) -> None:
    logger.info("Closing connection to database")

    app.state.db_client.close()

    logger.info("Connection closed")
