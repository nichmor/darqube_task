from typing import AsyncGenerator, Callable, Type

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from starlette.requests import Request

from app.db.repositories.base import BaseRepository


async def _get_connection(
        request: Request,
) -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    yield request.app.state.db


def get_repository(
        repo_type: Type[BaseRepository],
) -> Callable[[AsyncIOMotorDatabase], BaseRepository]:
    def _get_repo(
            conn: AsyncIOMotorDatabase = Depends(_get_connection),
    ) -> BaseRepository:
        return repo_type(conn)

    return _get_repo
