from app.models.common import ALLOWED_ROLES


def name_must_not_contain_space(value):
    if ' ' in value:
        raise ValueError('must not contain a space')
    return value


def validate_role(value):
    if value not in ALLOWED_ROLES:
        raise ValueError('role should be one of {}'.format(
            ','.join(ALLOWED_ROLES)
        ))
    return value
