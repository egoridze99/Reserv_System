from typing import TypedDict

from models import EmployeeRoleEnum


class UserJwtIdentity(TypedDict):
    id: int
    login: str
    role: EmployeeRoleEnum
    name: str
