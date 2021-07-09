from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from app.api.dependencies.auth import get_current_user_authorizer, verify_admin
from app.api.dependencies.database import get_repository
from app.core import config
from app.db.errors import EntityAlreadyExists
from app.db.repositories.users import UsersRepository
from app.models.schemas.users import UserProfile, UserUpdate
from app.models.users import User
from app.services import jwt
from app.services.authentication import check_first_last_name_is_taken
from app.services.users import (activate_user, deactivate_user,
                                update_user_by_id)

router = APIRouter()


@router.get(
    "",
    response_model=UserProfile,
    name="users:get-current-user"
)
async def get_current_user(
    user: User = Depends(get_current_user_authorizer()),
) -> UserProfile:
    token = jwt.create_access_token_for_user(user, str(config.SECRET_KEY))
    return UserProfile(
        **user.dict(exclude={'hashed_pass'}),
        token=token,
    )


@router.post(
    "/activate",
    response_model=UserProfile,
    name="users:activate-current-user"
)
async def activate_current_user(
    current_user: User = Depends(get_current_user_authorizer()),
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
) -> UserProfile:

    user_updated = await activate_user(current_user, users_repo)

    token = jwt.create_access_token_for_user(
        current_user,
        str(config.SECRET_KEY)
    )

    return UserProfile(
        **user_updated.dict(exclude={'hashed_pass'}),
        token=token,
    )


@router.post(
    "/deactivate",
    response_model=UserProfile,
    name="users:deactivate-current-user"
)
async def deactivate_current_user(
    current_user: User = Depends(get_current_user_authorizer()),
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
) -> UserProfile:

    user_updated = await deactivate_user(current_user, users_repo)

    token = jwt.create_access_token_for_user(
        current_user,
        str(config.SECRET_KEY)
    )

    return UserProfile(
        **user_updated.dict(exclude={'hashed_pass'}),
        token=token,
    )


@router.put(
    "",
    response_model=UserProfile,
    name="users:update-current-user"
)
async def update_current_user(
    user_update: UserUpdate = Body(..., embed=True, alias="user"),
    current_user: User = Depends(get_current_user_authorizer()),
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
) -> UserProfile:
    if (user_update.first_name and
            user_update.first_name != current_user.first_name):

        if await check_first_last_name_is_taken(
                users_repo,
                user_update.first_name,
                user_update.last_name,
        ):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
            )

    user = await users_repo.update_user(
        user=current_user,
        user_update=user_update
    )

    token = jwt.create_access_token_for_user(user, str(config.SECRET_KEY))

    return UserProfile(
        **user.dict(exclude={'hashed_pass'}),
        token=token,
    )


@router.post(
    "/admin/{user_id}",
    response_model=UserProfile,
    name="users:admin-update-user",
    dependencies=[Depends(verify_admin)]
)
async def admin_update_user(
    user_id: str,
    user_update: UserUpdate = Body(..., embed=True, alias="user"),
    current_user: User = Depends(get_current_user_authorizer()),
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
) -> UserProfile:

    if user_update.password:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
        )
    try:
        updated_user = await update_user_by_id(
            user_id,
            user_update,
            users_repo
        )

    except EntityAlreadyExists:

        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
        )
    token = jwt.create_access_token_for_user(
        current_user,
        str(config.SECRET_KEY)
    )

    return UserProfile(
        **updated_user.dict(
            exclude={'hashed_pass'},
        ),
        token=token,
    )
