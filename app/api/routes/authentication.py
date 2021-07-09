from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from app.api.dependencies.database import get_repository
from app.core import config
from app.db.errors import EntityDoesNotExist
from app.db.repositories.users import UsersRepository
from app.models.schemas.users import UserCreate, UserLogin, UserWithToken
from app.resources import error_messages
from app.services import jwt
from app.services.authentication import check_first_last_name_is_taken
from app.services.users import update_login_time

router = APIRouter()


@router.post(
    "",
    status_code=HTTP_201_CREATED,
    response_model=UserWithToken,
    name="auth:register",
)
async def register(
    user_create: UserCreate = Body(..., embed=True, alias="user"),
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
) -> UserWithToken:
    if await check_first_last_name_is_taken(
            users_repo,
            user_create.first_name,
            user_create.last_name
    ):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=error_messages.USER_EXIST,
        )

    user = await users_repo.create_user(user_create)

    token = jwt.create_access_token_for_user(user, str(config.SECRET_KEY))

    return UserWithToken(
        id=user.id,
        token=token
    )


@router.post(
    "/login",
    response_model=UserWithToken,
    name="auth:login"
)
async def login(
    user_login: UserLogin = Body(..., embed=True, alias="user"),
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
) -> UserWithToken:

    wrong_login_error = HTTPException(
        status_code=HTTP_400_BAD_REQUEST,
        detail=error_messages.LOGIN_FAILED,
    )

    try:
        user = await users_repo.get_user_by_first_last_name(
            first_name=user_login.first_name,
            last_name=user_login.last_name,
        )

    except EntityDoesNotExist as existence_error:
        raise wrong_login_error from existence_error

    if not user.check_password(user_login.password):
        raise wrong_login_error

    token = jwt.create_access_token_for_user(user, str(config.SECRET_KEY))

    await update_login_time(user, users_repo)

    return UserWithToken(
        id=user.id,
        token=token,
    )
