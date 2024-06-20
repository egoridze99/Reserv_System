from datetime import timedelta
from functools import reduce

from sqlalchemy import func
from sqlalchemy.orm import backref

from db import db
from models.entities.buisness import Transaction
from models.enums import TransactionTypeEnum, TransactionStatusEnum
from models.abstract import AbstractBaseModel


class Money(AbstractBaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, nullable=False, default=func.date(func.localtimestamp()))
    cashier_start = db.Column(db.Integer, nullable=False, default=0)

    cinema_id = db.Column(db.Integer, db.ForeignKey('cinema.id', name="cinema_id"))

    cinema = db.relationship("Cinema", backref=backref("money_records", uselist=True))
    transactions = db.relationship('Transaction', secondary='cashier_transaction_dict', cascade="all, delete")

    def __init__(cls, **kwargs):
        super().__init__(**kwargs)
        if 'date' in kwargs:
            date = kwargs['date']
            cinema_id = kwargs['cinema_id']
            previous_day = date - timedelta(days=1)

            if db.session.query(Money).count() == 0:
                cls.cashier_start = 0
                return

            min_date = db.session.query(func.min(Money.date)).one()[0]

            while True:
                if previous_day < min_date:
                    cls.cashier_start = 0
                    return

                previous_day_money_object = Money.query.filter(Money.cinema_id == cinema_id).filter(
                    str(previous_day) == Money.date).first()

                if previous_day_money_object is not None:
                    cls.cashier_start = previous_day_money_object.cashier_end
                    return

                previous_day -= timedelta(days=1)

    @property
    def income(cls):
        return reduce(lambda x, y: x + y.sum,
                      filter(lambda t: t.sum >= 0 and cls.__is_transaction_completed(t), cls.transactions), 0)

    @property
    def expense(cls):
        return reduce(lambda x, y: x + y.sum,
                      filter(lambda t: t.sum <= 0 and cls.__is_transaction_completed(t), cls.transactions), 0)

    @property
    def all_by_card(cls):
        return reduce(lambda x, y: x + y.sum, filter(
            lambda t: t.sum >= 0 and cls.__is_card_transaction(t) and cls.__is_transaction_completed(t),
            cls.transactions), 0)

    @property
    def all_by_cash(cls):
        return reduce(lambda x, y: x + y.sum, filter(
            lambda t: t.sum >= 0 and cls.__is_cash_transaction(t) and cls.__is_transaction_completed(t),
            cls.transactions), 0)

    @property
    def proceeds(cls):
        return cls.income + cls.expense

    @property
    def cashier_end(cls):
        return cls.cashier_start + cls.expense + cls.all_by_cash

    def __is_transaction_completed(cls, t: 'Transaction'):
        return t.transaction_status == TransactionStatusEnum.completed

    def __is_card_transaction(cls, t: 'Transaction'):
        return t.transaction_type == TransactionTypeEnum.card

    def __is_cash_transaction(cls, t: 'Transaction'):
        return t.transaction_type == TransactionTypeEnum.cash

    @staticmethod
    def to_json(money: 'Money'):
        return {
            "id": money.id,
            "date": money.date.strftime('%Y-%m-%d'),
            "income": money.income,
            "expense": money.expense,
            "proceeds": money.proceeds,
            "cashier_start": money.cashier_start,
            "cashier_end": money.cashier_end,
            "all_by_card": money.all_by_card,
            "all_by_cash": money.all_by_cash,
        }
