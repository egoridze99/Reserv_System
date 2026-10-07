from typing import Optional

from models import EmployeeRoleEnum, Certificate, Reservation, TransactionStatusEnum


def check_not_payment(role: EmployeeRoleEnum, reservation: 'Reservation', rent_price: int,
                      certificate: Optional["Certificate"]):
    if role == EmployeeRoleEnum.root.value:
        return False

    sum_of_transactions = sum(t.sum for t in reservation.transactions
                              if t.sum >= 0 and t.transaction_status == TransactionStatusEnum.completed)

    if certificate:
        sum_of_transactions += certificate.sum

    return sum_of_transactions < rent_price
