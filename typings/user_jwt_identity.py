from typing import TypedDict

from models import EmployeeRoleEnum, UserStatusEnum


class UserJwtIdentity(TypedDict):
    id: int
    login: str
    role: EmployeeRoleEnum
    name: str
    status: UserStatusEnum
