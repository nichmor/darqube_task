from typing import Callable, Optional

from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette import status

from app.api.dependencies.database import get_repository
from app.core.config import JWT_TOKEN_PREFIX, SECRET_KEY
from app.db.errors import EntityDoesNotExist
from app.db.repositories.users import UsersRepository
from app.models import common
from app.models.users import User
from app.services import jwt

HEADER_KEY = "Authorization"


def get_current_user_authorizer(
        *,
        required: bool = True
) -> Callable:  # type: ignore
    return _get_current_user if required else _get_current_user_optional


def _get_authorization_header_retriever(
    *,
    required: bool = True,
) -> Callable:  # type: ignore
    if required:
        return _get_authorization_header
    return _get_authorization_header_optional


def _get_authorization_header(
    api_key: str = Security(APIKeyHeader(name=HEADER_KEY)),
) -> str:
    try:
        token_prefix, token = api_key.split(" ")
    except ValueError:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
        )

    if token_prefix != JWT_TOKEN_PREFIX:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
        )

    return token


def _get_authorization_header_optional(
    authorization: Optional[str] = Security(
        APIKeyHeader(name=HEADER_KEY, auto_error=False),
    ),
) -> str:
    if authorization:
        return _get_authorization_header(authorization)

    return ""


async def _get_current_user(
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
    token: str = Depends(_get_authorization_header_retriever()),
) -> User:
    try:
        jwt_user = jwt.get_jwt_user_from_token(token, str(SECRET_KEY))
    except ValueError:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
        )

    try:
        return await users_repo.get_user_by_first_last_name(
            first_name=jwt_user.first_name,
            last_name=jwt_user.last_name
        )

    except EntityDoesNotExist:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
        )


async def _get_current_user_optional(
    repo: UsersRepository = Depends(get_repository(UsersRepository)),
    token: str = Depends(_get_authorization_header_retriever(required=False)),
) -> Optional[User]:
    if token:
        return await _get_current_user(repo, token)

    return None


def verify_admin(
        current_user: User = Depends(get_current_user_authorizer())
) -> User:

    if not current_user or current_user.role != common.ADMIN_ROLE:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
        )

    return current_user
