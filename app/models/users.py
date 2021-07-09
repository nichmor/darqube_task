from datetime import datetime

from pydantic import Field, validator

from app.models import validators
from app.models.rwmodel import OID, MongoModel
from app.services import security


class User(MongoModel):
    id: OID = Field(default=None, alias="_id")
    first_name: str = Field(min_length=3, max_length=50)
    last_name: str = Field(min_length=3, max_length=50)
    role: str
    is_active: bool = False
    created_at: datetime = None
    last_login: datetime = None
    hashed_pass: str = ''

    _validate_names = validator(
        'first_name',
        'last_name',
        allow_reuse=True
    )(validators.name_must_not_contain_space)

    _validate_role = validator(
        'role',
        allow_reuse=True
    )(validators.validate_role)

    @validator("created_at", pre=True)
    def default_datetime(
            cls,  # noqa: N805
            value: datetime,  # noqa: WPS110
    ) -> datetime:
        return value or datetime.now()

    def check_password(self, password: str) -> bool:
        return security.verify_password(password, self.hashed_pass)

    def set_password_hash(self, password: str) -> None:
        self.hashed_pass = security.get_password_hash(password)
