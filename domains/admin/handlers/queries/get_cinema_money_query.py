from sqlalchemy import func, not_, exists, and_

from db import db
from domains.admin.handlers.queries.get_reservation_money_query import sums_by_type
from models import TransactionStatusEnum, Transaction, Cinema, City, Reservation
from models.dictionaries import reservation_transaction_dict
from utils.parse_date import parse_shift_range


def get_cinema_money_query(until, till, is_income, is_refund=False):
    """Движение денег кинотеатра, не привязанное к резервам"""
    min_date, max_date = parse_shift_range(until, till)
    status = TransactionStatusEnum.refunded if is_refund else TransactionStatusEnum.completed

    rows = db.session.query(Cinema.id.label('cinema_id'), *sums_by_type()) \
        .select_from(Transaction) \
        .join(Cinema, Cinema.id == Transaction.cinema_id) \
        .join(City, City.id == Cinema.city_id) \
        .filter(func.datetime(Transaction.created_at, City.timezone).between(min_date, max_date)) \
        .filter(Transaction.transaction_status == status.value) \
        .filter(Transaction.sum > 0 if is_income else Transaction.sum < 0) \
        .filter(not_(exists().where(and_(Reservation.id == reservation_transaction_dict.c.reservation_id,
                                         Transaction.id == reservation_transaction_dict.c.transaction_id))
                     .correlate(Transaction))) \
        .group_by(Cinema.id).all()

    return {row.cinema_id: {"total": row.card + row.cash + row.sbp, "card": row.card, "cash": row.cash, "sbp": row.sbp}
            for row in rows}
