import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from app.db.repositories.users import UsersRepository
from app.models.users import User

pytestmark = pytest.mark.asyncio


async def test_user_success_registration(
        app: FastAPI,
        client: AsyncClient,
        connection: AsyncIOMotorClient,
        cleanup
) -> None:
    first_name, last_name, role, password = ["First",
                                             "Last",
                                             "dev",
                                             "pass"]
    registration_json = {
        "user": {
            "first_name": first_name,
            "last_name": last_name,
            "role": role,
            "password": password
        }
    }
    response = await client.post(
        app.url_path_for("auth:register"), json=registration_json
    )

    assert response.status_code == HTTP_201_CREATED

    repo = UsersRepository(connection)
    user = await repo.get_user_by_first_last_name(
        first_name=first_name,
        last_name=last_name,
    )
    assert user.first_name == first_name
    assert user.last_name == last_name
    assert user.role == role
    assert user.check_password(password)


async def test_failed_user_registration_when_credentials_are_taken(
    app: FastAPI,
    client: AsyncClient,
    test_user: User,
) -> None:
    registration_json = {
        "user": {
            "first_name": test_user.first_name,
            "last_name": test_user.last_name,
            "role": test_user.role,
            "password": "test password"
        }
    }

    response = await client.post(
        app.url_path_for("auth:register"), json=registration_json
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
