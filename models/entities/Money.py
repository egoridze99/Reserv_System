from datetime import datetime, timedelta

from sqlalchemy import select, func

from db import db
from models.abstract import AbstractBaseModel
from models.entities.Cinema import Cinema


class Money(AbstractBaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, nullable=False, default=func.date(func.localtimestamp()))
    income = db.Column(db.Integer, nullable=False, default=0)
    expense = db.Column(db.Integer, nullable=False, default=0)
    proceeds = db.Column(db.Integer, nullable=False, default=0)
    cashier_start = db.Column(db.Integer, nullable=False, default=0)
    cashier_end = db.Column(db.Integer, nullable=False, default=0)
    all_by_card = db.Column(db.Integer, nullable=False, default=0)
    all_by_cash = db.Column(db.Integer, nullable=False, default=0)
    cinema_id = db.Column(db.Integer, db.ForeignKey('cinema.id', name="cinema_id"))

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

    def __str__(self):
        return f"""
        <Деньги date={self.date} 
        income={self.income} 
        expense = {self.expense}
        proceeds = {self.proceeds}
        cashier_start = {self.cashier_start}
        cashier_end = {self.cashier_end}
        all_by_card = {self.all_by_card}
        all_by_cash = {self.all_by_cash}>
        """

    @staticmethod
    def to_json(money: 'Money'):
        return {
            "id": money.id,
            "date": money.date,
            "income": money.income,
            "expense": money.expense,
            "proceeds": money.proceeds,
            "cashier_start": money.cashier_start,
            "cashier_end": money.cashier_end,
            "all_by_card": money.all_by_card,
            "all_by_cash": money.all_by_cash,
            "cinema": Cinema.to_json(money.cinema),
        }
