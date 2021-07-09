import pytest
from bson import ObjectId
from pydantic import ValidationError

from app.models.users import User


def test_from_mongo_return_id_field():
    user_from_mongo = User(
        id=ObjectId(),
        first_name='test',
        last_name='test',
        role='dev',
        is_active=True,
        hashed_pass='test_pass'
    )

    mongo_dict = user_from_mongo.mongo()
    assert '_id' in mongo_dict


def test_role_validation():
    with pytest.raises(ValidationError):
        User(
            id=ObjectId(),
            first_name='test',
            last_name='test',
            role='wrong role',
            is_active=True,
            hashed_pass='test_pass'
        )


def test_first_name_validation():
    with pytest.raises(ValidationError):
        User(
            id=ObjectId(),
            first_name='test Test',
            last_name='Test',
            role='dev',
            is_active=True,
            hashed_pass='test_pass'
        )


def test_last_name_validation():
    with pytest.raises(ValidationError):
        User(
            id=ObjectId(),
            first_name='Test',
            last_name='Test Test',
            role='dev',
            is_active=True,
            hashed_pass='test_pass'
        )
