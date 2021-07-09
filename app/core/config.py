from typing import List

from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings, Secret

API_PREFIX = "/api"

JWT_TOKEN_PREFIX = "Token"  # noqa: S105
VERSION = "1.0.0"

config = Config(".env")


DEBUG: bool = config("DEBUG", cast=bool, default=False)

MONGO_URI: str = config("MONGO_URI")
MONGO_DATABASE: str = config("MONGO_DATABASE")
MONGO_USERS_COLLECTION: str = config("MONGO_USERS_COLLECTION")

MAX_CONNECTIONS_COUNT: int = config(
    "MAX_CONNECTIONS_COUNT",
    cast=int,
    default=10
)
MIN_CONNECTIONS_COUNT: int = config(
    "MIN_CONNECTIONS_COUNT",
    cast=int,
    default=10
)

SECRET_KEY: Secret = config(
    "SECRET_KEY",
    cast=Secret
)

PROJECT_NAME: str = config(
    "PROJECT_NAME",
    default="Darqube API"
)

ALLOWED_HOSTS: List[str] = config(
    "ALLOWED_HOSTS",
    cast=CommaSeparatedStrings,
    default="",
)
