from typing import List

from models import Transaction


def get_sum_of_checkouts(checkouts: List['Transaction']) -> int:
    sum_of_checkouts = 0

    for checkout in checkouts:
        sum_of_checkouts += int(checkout.sum)

    return sum_of_checkouts
