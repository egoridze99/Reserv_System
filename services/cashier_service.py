from datetime import datetime, time, timedelta

from sqlalchemy import func, case, and_

from db import db
from models import Transaction, Cinema, TransactionStatusEnum, TransactionTypeEnum
from utils.convert_tz import convert_tz


def _sum_if(condition):
    return func.sum(case([(condition, Transaction.sum)], else_=0))


def get_cashier_info(date: datetime.date, cinema_id: int):
    """Касса кинотеатра за смену: с 8:00 date до 8:00 следующего дня по местному времени"""
    cinema = Cinema.query.filter(Cinema.id == cinema_id).first()
    min_date = convert_tz(datetime.combine(date, time(8)), cinema.city.timezone, True)
    max_date = convert_tz(datetime.combine(date + timedelta(days=1), time(8)), cinema.city.timezone, True)

    completed = db.session.query(Transaction) \
        .filter(Transaction.cinema_id == cinema_id) \
        .filter(Transaction.transaction_status == TransactionStatusEnum.completed)

    is_income = Transaction.sum >= 0
    income, expense, all_by_cash, all_by_card, all_by_sbp = (value or 0 for value in completed.with_entities(
        _sum_if(is_income),
        _sum_if(Transaction.sum < 0),
        _sum_if(and_(is_income, Transaction.transaction_type == TransactionTypeEnum.cash)),
        _sum_if(and_(is_income, Transaction.transaction_type == TransactionTypeEnum.card)),
        _sum_if(and_(is_income, Transaction.transaction_type == TransactionTypeEnum.sbp)),
    ).filter(Transaction.created_at.between(min_date, max_date)).one())

    cashier_start = completed.with_entities(func.sum(Transaction.sum)) \
        .filter(Transaction.created_at < min_date) \
        .filter(Transaction.transaction_type == TransactionTypeEnum.cash) \
        .scalar() or 0

    return {
        "income": income,
        "expense": expense,
        "proceeds": income + expense,
        "all_by_cash": all_by_cash,
        "all_by_card": all_by_card,
        "all_by_sbp": all_by_sbp,
        "cashier_start": cashier_start,
        "cashier_end": cashier_start + expense + all_by_cash
    }
