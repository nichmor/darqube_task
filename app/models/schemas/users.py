from datetime import datetime

from pydantic import BaseModel, Field, validator

from app.models import validators
from app.models.rwmodel import OID, MongoModel


class UserLogin(BaseModel):
    first_name: str = Field(min_length=3, max_length=50)
    last_name: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=4, max_length=20)

    _validate_names = validator(
        'first_name',
        'last_name',
        allow_reuse=True
    )(validators.name_must_not_contain_space)


class UserCreate(UserLogin):
    role: str

    _validate_role = validator(
        'role',
        allow_reuse=True
    )(validators.validate_role)


class UserUpdate(BaseModel):
    first_name: str = None
    last_name: str = None
    password: str = None
    role: str = None

    _validate_role = validator(
        'role',
        allow_reuse=True
    )(validators.validate_role)


class UserWithToken(MongoModel):
    id: OID = Field()
    token: str


class UserProfile(MongoModel):
    id: OID = Field()
    first_name: str
    last_name: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: datetime = None
    token: str = None
