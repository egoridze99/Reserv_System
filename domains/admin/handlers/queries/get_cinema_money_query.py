from datetime import datetime, time, timedelta
from functools import reduce

from sqlalchemy import func, case, not_, exists, and_

from db import db
from models import TransactionTypeEnum, TransactionStatusEnum, Transaction, Cinema, City, Reservation, Room
from models.dictionaries import reservation_transaction_dict


def get_cinema_money_query(until, till, is_income, is_refund=False):
    session = db.session

    until = datetime.strptime(until, "%Y-%m-%d")
    if till:
        till = datetime.strptime(till, "%Y-%m-%d")

    min_date = datetime.combine(until, time(8))
    max_date = datetime.combine(till + timedelta(days=1), time(8))

    subquery = session.query(
        Cinema.id.label('cinema_id'),
        func.sum(case([(Transaction.transaction_type == TransactionTypeEnum.card.value, Transaction.sum)],
                      else_=0)).label('card'),
        func.sum(case([(Transaction.transaction_type == TransactionTypeEnum.cash.value, Transaction.sum)],
                      else_=0)).label('cash'),
        func.sum(
            case([(Transaction.transaction_type == TransactionTypeEnum.sbp.value, Transaction.sum)], else_=0)).label(
            'sbp')
    ).select_from(Transaction).join(
        Cinema, Cinema.id == Transaction.cinema_id
    ).join(
        City, City.id == Cinema.city_id
    ).outerjoin(reservation_transaction_dict, Transaction.id == reservation_transaction_dict.c.transaction_id
                ).outerjoin(Reservation, reservation_transaction_dict.c.reservation_id == Reservation.id
                            ).filter(
        func.datetime(Transaction.created_at, City.timezone).between(min_date, max_date)
    ).filter(Transaction.transaction_status == (
        TransactionStatusEnum.refunded.value if is_refund else TransactionStatusEnum.completed.value)) \
        .filter(Transaction.sum > 0 if is_income else Transaction.sum < 0) \
        .filter(not_(exists().where(and_(Reservation.id == reservation_transaction_dict.c.reservation_id,
                                         Transaction.id == reservation_transaction_dict.c.transaction_id)).correlate(
        Transaction))) \
        .group_by(Cinema.id).subquery()

    data = session.query(
        subquery.c.cinema_id,
        subquery.c.card,
        subquery.c.cash,
        subquery.c.sbp,
        (func.coalesce(subquery.c.card, 0) + func.coalesce(subquery.c.cash, 0) + func.coalesce(subquery.c.sbp,
                                                                                               0)).label('sum')
    ).select_from(subquery).all()

    data = filter(lambda i: i.cinema_id is not None, data)

    result = {}

    for item in data:
        result[item.cinema_id] = {
            "total": item.card + item.cash + item.sbp,
            "card": item.card,
            "cash": item.cash,
            "sbp": item.sbp,
        }

    return result
