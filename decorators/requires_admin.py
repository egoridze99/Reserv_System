from functools import wraps

from flask import abort
from flask_jwt_extended import get_jwt_identity

from models import EmployeeRoleEnum
from typings import UserJwtIdentity


def requires_admin(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        jwt_identity: UserJwtIdentity = get_jwt_identity()

        if EmployeeRoleEnum[jwt_identity["role"]] != EmployeeRoleEnum.root:
            return abort(403)

        return fn(*args, **kwargs)

    return wrapper
