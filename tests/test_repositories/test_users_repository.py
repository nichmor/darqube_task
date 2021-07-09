import pytest
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.repositories.users import UsersRepository
from app.models.schemas.users import UserCreate, UserUpdate
from app.services.security import verify_password

pytestmark = pytest.mark.asyncio


async def test_repository_can_create_user(
        connection: AsyncIOMotorDatabase,
        cleanup
):
    repo = UsersRepository(connection)

    user = UserCreate(
        first_name="First",
        last_name="Last",
        role="admin",
        password="test password"
    )

    user_db = await repo.create_user(user)

    assert user_db.id is not None

    assert user.first_name == user_db.first_name
    assert user.last_name == user_db.last_name
    assert user.role == user_db.role
    assert verify_password(user.password, user_db.hashed_pass)


async def test_repository_update_user(
        connection: AsyncIOMotorDatabase,
        cleanup
):
    repo = UsersRepository(connection)

    user = UserCreate(
        first_name="First",
        last_name="Last",
        role="admin",
        password="test password"
    )

    new_user = await repo.create_user(user)

    update_user = UserUpdate(
        first_name="Updated"
    )

    updated_user = await repo.update_user(
        new_user,
        update_user
    )

    assert updated_user.first_name == "Updated"
    assert updated_user.last_name == new_user.last_name
