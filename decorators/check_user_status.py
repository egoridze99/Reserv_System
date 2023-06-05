from functools import wraps

from flask import abort
from flask_jwt_extended import get_jwt_identity

from models import UserStatusEnum
from typings import UserJwtIdentity


def check_user_status(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        jwt_identity: UserJwtIdentity = get_jwt_identity()

        if UserStatusEnum[jwt_identity["status"]] == UserStatusEnum.deprecated:
            return abort(401)

        return fn(*args, **kwargs)

    return wrapper
