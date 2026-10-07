from sqlalchemy import func, case

from db import db
from models import TransactionTypeEnum, TransactionStatusEnum, Transaction, Cinema, City, Reservation, Room
from models.dictionaries import reservation_transaction_dict
from utils.parse_date import parse_shift_range


def sums_by_type():
    return [func.sum(case([(Transaction.transaction_type == t.value, Transaction.sum)], else_=0)).label(t.value)
            for t in (TransactionTypeEnum.card, TransactionTypeEnum.cash, TransactionTypeEnum.sbp)]


def get_reservation_money_query(until, till, is_income, is_refund=False):
    min_date, max_date = parse_shift_range(until, till)
    status = TransactionStatusEnum.refunded if is_refund else TransactionStatusEnum.completed

    rows = db.session.query(Cinema.id.label('cinema_id'), Room.id.label('room_id'), *sums_by_type()) \
        .select_from(Transaction) \
        .join(Cinema, Cinema.id == Transaction.cinema_id) \
        .join(City, City.id == Cinema.city_id) \
        .join(reservation_transaction_dict, reservation_transaction_dict.c.transaction_id == Transaction.id) \
        .join(Reservation, Reservation.id == reservation_transaction_dict.c.reservation_id) \
        .join(Room, Room.id == Reservation.room_id) \
        .filter(func.datetime(Reservation.date, City.timezone).between(min_date, max_date)) \
        .filter(Transaction.transaction_status == status.value) \
        .filter(Transaction.sum > 0 if is_income else Transaction.sum < 0) \
        .group_by(Room.id).group_by(Cinema.id).all()

    result = {}

    for row in rows:
        room = {"card": row.card, "cash": row.cash, "sbp": row.sbp, "total": row.card + row.cash + row.sbp}
        cinema = result.setdefault(row.cinema_id, {"cinema_id": row.cinema_id, "card": 0, "cash": 0, "sbp": 0,
                                                   "total": 0, "rooms": {}})
        cinema["rooms"][row.room_id] = room

        for key in ("card", "cash", "sbp", "total"):
            cinema[key] += room[key]

    return result
