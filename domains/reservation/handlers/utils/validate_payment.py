from typing import Optional

from models import EmployeeRoleEnum, Certificate, ReservationStatusEnum


def validate_payment(role: EmployeeRoleEnum, data, certificate: Optional["Certificate"]):
    if role == EmployeeRoleEnum.root.name \
            or data['status'] != ReservationStatusEnum.finished.name:
        return True

    certificate_sum = certificate.sum if certificate else 0

    sum_of_payments = data['card'] + data['cash'] + data['rent'] + certificate_sum

    return sum_of_payments >= data['rent']
