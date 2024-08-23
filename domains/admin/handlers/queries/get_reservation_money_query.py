from datetime import datetime, time, timedelta
from functools import reduce

from sqlalchemy import func, case

from db import db
from models import TransactionTypeEnum, TransactionStatusEnum, Transaction, Cinema, City, Reservation, Room
from models.dictionaries import reservation_transaction_dict


def get_reservation_money_query(until, till, is_income, is_refund=False):
    session = db.session

    until = datetime.strptime(until, "%Y-%m-%d")
    if till:
        till = datetime.strptime(till, "%Y-%m-%d")

    min_date = datetime.combine(until, time(8))
    max_date = datetime.combine(till + timedelta(days=1), time(8))

    subquery = session.query(
        Cinema.id.label('cinema_id'),
        Room.id.label('room_id'),
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
    ).join(
        reservation_transaction_dict, reservation_transaction_dict.c.transaction_id == Transaction.id
    ).join(
        Reservation, Reservation.id == reservation_transaction_dict.c.reservation_id
    ).join(
        Room, Room.id == Reservation.room_id
    ).filter(
        func.datetime(Reservation.date, City.timezone).between(min_date, max_date)
    ).filter(Transaction.transaction_status == (
        TransactionStatusEnum.refunded.value if is_refund else TransactionStatusEnum.completed.value)) \
        .filter(Transaction.sum > 0 if is_income else Transaction.sum < 0).group_by(Room.id).subquery()

    data = session.query(
        subquery.c.cinema_id,
        subquery.c.room_id,
        subquery.c.card,
        subquery.c.cash,
        subquery.c.sbp,
        (func.coalesce(subquery.c.card, 0) + func.coalesce(subquery.c.cash, 0) + func.coalesce(subquery.c.sbp,
                                                                                               0)).label('sum')
    ).select_from(subquery).all()

    data = filter(lambda i: i.cinema_id is not None, data)

    result_grouped_by_cinema_id = {}

    for row in data:
        if row.cinema_id not in result_grouped_by_cinema_id:
            result_grouped_by_cinema_id[row.cinema_id] = []

        result_grouped_by_cinema_id[row.cinema_id].append(row)

    result = {}

    for cinema_id, rooms in result_grouped_by_cinema_id.items():
        result[cinema_id] = {
            "cinema_id": cinema_id,
            "card": sum([room.card for room in rooms]),
            "cash": sum([room.cash for room in rooms]),
            "sbp": sum([room.sbp for room in rooms]),
        }

        for room in rooms:
            if 'rooms' not in result[cinema_id]:
                result[cinema_id]['rooms'] = {}

            result[cinema_id]['rooms'][room.room_id] = {"card": room.card,
                                                        "cash": room.cash,
                                                        "sbp": room.sbp, "total": room.card +
                                                                                  room.cash +
                                                                                  room.sbp}

        result[cinema_id]['total'] = result[cinema_id]['cash'] + result[cinema_id]['card'] + result[cinema_id]['sbp']

    return result
