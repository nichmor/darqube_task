import uuid
import warnings
from os import getenv

import docker as libdocker
import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core import config
from app.db.repositories.users import UsersRepository
from app.models.schemas.users import UserCreate
from app.models.users import User
from app.services import jwt
from tests.utils import pull_image

MONGO_DOCKER_IMAGE = "mongo:4.2.2"

USE_LOCAL_DB = getenv("USE_LOCAL_DB_FOR_TEST", False)


@pytest.fixture(scope="session")
def docker() -> libdocker.APIClient:
    with libdocker.APIClient(version="auto") as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
def mongo_db(docker: libdocker.APIClient) -> None:
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    if not USE_LOCAL_DB:  # pragma: no cover
        pull_image(docker, MONGO_DOCKER_IMAGE)

        container = docker.create_container(
            image=MONGO_DOCKER_IMAGE,
            name="test-mongo-{}".format(uuid.uuid4()),
            detach=True,
            ports=[27017],
            host_config=docker.create_host_config(
                port_bindings={
                    27017: 27018
                }
            )
        )
        docker.start(container=container["Id"])

        dsn = "mongodb://localhost:27018"

        try:
            config.MONGO_URI = dsn
            yield container
        finally:
            docker.kill(container["Id"])
            docker.remove_container(container["Id"])
    else:  # pragma: no cover
        yield
        return


@pytest.fixture
def app(mongo_db) -> FastAPI:
    from app.main import get_application

    return get_application()


@pytest.fixture
async def initialized_app(app: FastAPI) -> FastAPI:
    async with LifespanManager(app):
        yield app


@pytest.fixture
def connection(initialized_app: FastAPI) -> AsyncIOMotorDatabase:
    return initialized_app.state.db


@pytest.fixture
async def cleanup(connection: AsyncIOMotorDatabase):
    yield
    await connection.drop_collection(config.MONGO_USERS_COLLECTION)


@pytest.fixture
async def test_user(
    connection: AsyncIOMotorDatabase,
    cleanup,
) -> User:
    user = UserCreate(
        first_name="First",
        last_name="Last",
        password="Test Password",
        role="dev",
    )

    return await UsersRepository(connection).create_user(
        user
    )


@pytest.fixture
async def admin_user(
    connection: AsyncIOMotorDatabase,
    cleanup,
) -> User:
    user = UserCreate(
        first_name="Admin",
        last_name="Admin",
        password="Admin Password",
        role="admin",
    )
    return await UsersRepository(connection).create_user(
        user
    )


@pytest.fixture
async def client(initialized_app: FastAPI) -> AsyncClient:
    async with AsyncClient(
        app=initialized_app,
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client


@pytest.fixture
def token(test_user: User) -> str:
    return jwt.create_access_token_for_user(test_user, str(config.SECRET_KEY))


@pytest.fixture
def admin_token(admin_user: User) -> str:
    return jwt.create_access_token_for_user(admin_user, str(config.SECRET_KEY))


@pytest.fixture
def authorization_prefix() -> str:
    from app.core.config import JWT_TOKEN_PREFIX

    return JWT_TOKEN_PREFIX


@pytest.fixture
def authorized_client(
    client: AsyncClient,
    token: str,
    authorization_prefix: str
) -> AsyncClient:
    client.headers = {
        "Authorization": f"{authorization_prefix} {token}",
        **client.headers,
    }
    return client


@pytest.fixture
def authorized_admin_client(
    client: AsyncClient,
    admin_token: str,
    authorization_prefix: str
) -> AsyncClient:
    client.headers = {
        "Authorization": f"{authorization_prefix} {admin_token}",
        **client.headers,
    }

    return client
