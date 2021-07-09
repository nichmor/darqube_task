from app.db.errors import EntityDoesNotExist
from app.db.repositories.users import UsersRepository


async def check_first_last_name_is_taken(
        repo: UsersRepository,
        first_name: str,
        last_name: str,
) -> bool:
    try:
        await repo.get_user_by_first_last_name(
            first_name=first_name,
            last_name=last_name,
        )
    except EntityDoesNotExist:
        return False

    return True
