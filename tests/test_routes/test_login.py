import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from app.models.users import User

pytestmark = pytest.mark.asyncio


async def test_user_successful_login(
    app: FastAPI,
    client: AsyncClient,
    test_user: User
) -> None:
    login_json = {
        "user": {
            "first_name": test_user.first_name,
            "last_name": test_user.last_name,
            "role": test_user.role,
            "password": "Test Password"
        }
    }

    response = await client.post(
        app.url_path_for("auth:login"),
        json=login_json
    )
    assert response.status_code == HTTP_200_OK


async def test_user_login_failed_user_does_not_exist(
    app: FastAPI,
    client: AsyncClient,
    test_user: User,
) -> None:
    login_json = {
        "user": {
            "first_name": "{}_failed".format(test_user.first_name),
            "last_name": test_user.last_name,
            "role": test_user.role,
            "password": "Test Password"
        }
    }

    response = await client.post(
        app.url_path_for("auth:login"),
        json=login_json
    )
    assert response.status_code == HTTP_400_BAD_REQUEST


async def test_user_login_failed_password_mismatch(
    app: FastAPI,
    client: AsyncClient,
    test_user: User,
) -> None:
    login_json = {
        "user": {
            "first_name": test_user.first_name,
            "last_name": test_user.last_name,
            "role": test_user.role,
            "password": "abasdasd"
        }
    }

    response = await client.post(
        app.url_path_for("auth:login"),
        json=login_json
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
