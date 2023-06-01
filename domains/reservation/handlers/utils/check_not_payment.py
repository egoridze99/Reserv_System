from typing import Optional

from models import EmployeeRoleEnum, Certificate, ReservationStatusEnum


def check_not_payment(role: EmployeeRoleEnum, data, certificate: Optional["Certificate"]):
    return data['card'] == 0 \
            and data['cash'] == 0 \
            and data['status'] == ReservationStatusEnum.finished.name \
            and data['rent'] != 0 \
            and not certificate \
            and role != EmployeeRoleEnum.root.name
