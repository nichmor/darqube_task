from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument

from app.core.config import MONGO_USERS_COLLECTION
from app.db.errors import EntityDoesNotExist
from app.db.repositories.base import BaseRepository
from app.models.schemas.users import UserCreate, UserUpdate
from app.models.users import User


class UsersRepository(BaseRepository):
    def __init__(self, client: AsyncIOMotorDatabase):
        super().__init__(client)
        self.collection = self.connection[MONGO_USERS_COLLECTION]

    async def get_user_by_id(
        self,
        user_id: str
    ) -> User:
        user = await self.collection.find_one(
            filter={'_id': ObjectId(user_id)}
        )

        if user:
            return User(**user)

        raise EntityDoesNotExist(
            "user does not exist"
        )

    async def get_user_by_first_last_name(
        self,
        first_name,
        last_name
    ) -> User:
        user = await self.collection.find_one(
            filter={'first_name': first_name, 'last_name': last_name}
        )

        if user:
            return User(**user)

        raise EntityDoesNotExist(
            "user does not exist"
        )

    async def create_user(
        self,
        user_registration: UserCreate
    ) -> User:
        user = User(
            **user_registration.dict()
        )

        user.set_password_hash(user_registration.password)

        user.is_active = False

        result = await self.collection.insert_one(
            document=user.dict(exclude={"id"})
        )

        user_db = User(
            **user.dict(exclude={"id"}),
            id=result.inserted_id
        )

        return user_db

    async def update_by_fields(
        self,
        user: User,
        data: dict,
    ) -> User:

        updated = await self.collection.find_one_and_update(
            filter={'_id': user.id},
            update={'$set': data},
            return_document=ReturnDocument.AFTER
        )

        return User(**updated)

    async def update_user(
        self,
        user: User,
        user_update: UserUpdate
    ) -> User:

        doc_to_be_updated = user_update.dict(
            exclude_unset=True
        )

        if user_update.password:
            user.set_password_hash(user_update.password)
            doc_to_be_updated['hashed_pass'] = user.hashed_pass

        updated = await self.collection.find_one_and_update(
            filter={'_id': user.id},
            update={'$set': doc_to_be_updated},
            return_document=ReturnDocument.AFTER
        )

        return User(**updated)
