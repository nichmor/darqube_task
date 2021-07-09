from datetime import datetime, timedelta
from typing import Dict

import jwt
from pydantic import ValidationError

from app.models.schemas.jwt import JWTMeta, JWTUser
from app.models.users import User

JWT_SUBJECT = "access"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # one week


def create_jwt_token(
    *,
    jwt_content: Dict[str, str],
    secret_key: str,
    expires_delta: timedelta,
) -> str:
    to_encode = jwt_content.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update(JWTMeta(exp=expire, sub=JWT_SUBJECT).dict())
    return jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)


def create_access_token_for_user(user: User, secret_key: str) -> str:
    return create_jwt_token(
        jwt_content=JWTUser(
            first_name=user.first_name,
            last_name=user.last_name,
        ).dict(),
        secret_key=secret_key,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def get_jwt_user_from_token(token: str, secret_key: str) -> JWTUser:
    try:
        return JWTUser(**jwt.decode(token, secret_key, algorithms=[ALGORITHM]))
    except jwt.PyJWTError as decode_error:
        raise ValueError("unable to decode JWT token") from decode_error
    except ValidationError as validation_error:
        raise ValueError("malformed payload in token") from validation_error
