from datetime import time, timedelta
from typing import Optional

from db import db
from models import Money, Transaction
from utils.convert_tz import convert_tz


def add_transaction_to_cashier(transaction: 'Transaction') -> Optional[Money]:
    transaction_date_local = convert_tz(transaction.created_at, transaction.cinema.city.timezone, False)

    cashier_date = transaction_date_local.date()
    if transaction_date_local.time() < time(8):
        cashier_date = cashier_date - timedelta(days=1)

    money_record = Money.query.filter(Money.date == cashier_date).filter(
        Money.cinema_id == transaction.cinema_id).first()

    if money_record is None:
        money_record = Money(date=cashier_date, cinema_id=transaction.cinema_id)
        money_record.transactions.append(transaction)
    else:
        money_record.transactions.append(transaction)

    try:
        db.session.add(money_record)
        db.session.commit()
        return money_record
    except:
        return None
