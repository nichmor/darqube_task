from datetime import datetime

from app.db.errors import EntityAlreadyExists
from app.db.repositories.users import UsersRepository
from app.models.schemas.users import UserUpdate
from app.models.users import User
from app.services.authentication import check_first_last_name_is_taken


async def update_login_time(
        user: User,
        user_repo: UsersRepository
):
    current_time = datetime.now()
    await user_repo.update_by_fields(
        user,
        {'last_login': current_time}
    )


async def activate_user(
        user: User,
        user_repo: UsersRepository
) -> User:
    return await user_repo.update_by_fields(
        user,
        {'is_active': True}
    )


async def deactivate_user(
        user: User,
        user_repo: UsersRepository
) -> User:
    return await user_repo.update_by_fields(
        user,
        {'is_active': False}
    )


async def _update_user(
        present_user: User,
        user_update: UserUpdate,
        users_repo: UsersRepository
):
    if (user_update.first_name
            and user_update.first_name != present_user.first_name):
        if await check_first_last_name_is_taken(
                users_repo,
                user_update.first_name,
                user_update.last_name,
        ):
            raise EntityAlreadyExists()

    user = await users_repo.update_user(
        user=present_user,
        user_update=user_update
    )

    return user


async def update_user(
        user_update: UserUpdate,
        current_user: User,
        users_repo: UsersRepository,
) -> User:
    return await _update_user(
        current_user,
        user_update,
        users_repo,
    )


async def update_user_by_id(
        user_id: str,
        user_update: UserUpdate,
        users_repo: UsersRepository,
) -> User:
    present_user = await users_repo.get_user_by_id(user_id)

    return await _update_user(
        present_user,
        user_update,
        users_repo
    )
