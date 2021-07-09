import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.status import (HTTP_200_OK, HTTP_400_BAD_REQUEST,
                              HTTP_403_FORBIDDEN)

from app.db.repositories.users import UsersRepository
from app.models.schemas.users import UserProfile, UserWithToken
from app.models.users import User

pytestmark = pytest.mark.asyncio


@pytest.fixture(params=("", "JWT value"))
def wrong_authorization_header(request) -> str:
    return request.param


@pytest.mark.parametrize(
    "api_method, route_name",
    (("GET", "users:get-current-user"), ("PUT", "users:update-current-user")),
)
async def test_user_can_not_access_own_profile_if_not_logged_in(
    app: FastAPI,
    client: AsyncClient,
    test_user: User,
    api_method: str,
    route_name: str,
) -> None:
    response = await client.request(api_method, app.url_path_for(route_name))
    assert response.status_code == HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "api_method, route_name",
    (("GET", "users:get-current-user"), ("PUT", "users:update-current-user")),
)
async def test_user_can_not_retrieve_own_profile_if_wrong_token(
    app: FastAPI,
    client: AsyncClient,
    test_user: User,
    api_method: str,
    route_name: str,
    wrong_authorization_header: str,
) -> None:
    response = await client.request(
        api_method,
        app.url_path_for(route_name),
        headers={"Authorization": wrong_authorization_header},
    )
    assert response.status_code == HTTP_403_FORBIDDEN


async def test_user_can_retrieve_own_profile(
    app: FastAPI,
    authorized_client: AsyncClient,
    test_user: User,
    token: str
) -> None:
    response = await authorized_client.get(app.url_path_for(
        "users:get-current-user"
    ))
    assert response.status_code == HTTP_200_OK

    user_profile = UserWithToken(**response.json())

    assert str(user_profile.id) == str(test_user.id)


async def test_user_can_change_password(
    app: FastAPI,
    authorized_client: AsyncClient,
    test_user: User,
    token: str,
    connection: AsyncIOMotorClient,
) -> None:
    response = await authorized_client.put(
        app.url_path_for("users:update-current-user"),
        json={"user": {"password": "new_test_password"}},
    )
    assert response.status_code == HTTP_200_OK
    user_profile = UserProfile(**response.json())

    users_repo = UsersRepository(connection)
    user = await users_repo.get_user_by_first_last_name(
        first_name=user_profile.first_name,
        last_name=user_profile.last_name,
    )

    assert user.check_password("new_test_password")


async def test_user_can_change_first_name_if_not_taken(
    app: FastAPI,
    authorized_client: AsyncClient,
    test_user: User,
    token: str,
    connection: AsyncIOMotorClient,
) -> None:

    response = await authorized_client.put(
        app.url_path_for("users:update-current-user"),
        json={"user": {"first_name": "Foo"}},
    )
    assert response.status_code == HTTP_200_OK
    user_profile = UserProfile(**response.json())

    users_repo = UsersRepository(connection)
    user = await users_repo.get_user_by_first_last_name(
        first_name=user_profile.first_name,
        last_name=user_profile.last_name,
    )

    assert user.first_name == "Foo"


async def test_user_can_activate_itself(
    app: FastAPI,
    authorized_client: AsyncClient,
    test_user: User,
    token: str,
    connection: AsyncIOMotorClient,
) -> None:

    response = await authorized_client.post(
        app.url_path_for("users:activate-current-user"),
    )

    assert response.status_code == HTTP_200_OK
    user_profile = UserProfile(**response.json())

    assert user_profile.is_active is True


async def test_user_can_deactivate_itself(
    app: FastAPI,
    authorized_client: AsyncClient,
    test_user: User,
    token: str,
    connection: AsyncIOMotorClient,
) -> None:

    response = await authorized_client.post(
        app.url_path_for("users:deactivate-current-user"),
    )

    assert response.status_code == HTTP_200_OK
    user_profile = UserProfile(**response.json())

    assert user_profile.is_active is False


async def test_admin_can_update_other_user(
    app: FastAPI,
    authorized_admin_client: AsyncClient,
    test_user: User,
    admin_user: User,
    token: str,
    connection: AsyncIOMotorClient,
) -> None:

    changed_first_name = "Changed"

    response = await authorized_admin_client.post(
        app.url_path_for(
            "users:admin-update-user",
            **{"user_id": str(test_user.id)}
         ),
        json={"user": {"first_name": changed_first_name}},
    )

    assert response.status_code == HTTP_200_OK
    user_profile = UserProfile(**response.json())

    assert user_profile.first_name == changed_first_name
    assert str(user_profile.id) == str(test_user.id)


async def test_admin_can_not_update_other_user_password(
    app: FastAPI,
    authorized_admin_client: AsyncClient,
    test_user: User,
    admin_user: User,
    token: str,
    connection: AsyncIOMotorClient,
) -> None:

    response = await authorized_admin_client.post(
        app.url_path_for(
            "users:admin-update-user",
            **{"user_id": str(test_user.id)}
         ),
        json={"user": {"password": "12312"}},
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
