from datetime import date, datetime, timedelta, time

import shortuuid
from sqlalchemy import func
from sqlalchemy.orm import backref

from db import db
from models.abstract import AbstractBaseModel
from models.entities.buisness.User import User
from models.enums import TransactionStatusEnum, TransactionTypeEnum
from utils.convert_tz import convert_tz


class Transaction(AbstractBaseModel):
    __tablename__ = 'transaction'

    id = db.Column(db.String, primary_key=True)
    created_at = db.Column(db.DateTime, default=func.localtimestamp(), nullable=False)

    sum = db.Column(db.Integer, nullable=False)
    alias = db.Column(db.String)
    description = db.Column(db.String)

    cinema_id = db.Column(db.Integer, db.ForeignKey('cinema.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    transaction_type = db.Column(db.Enum(TransactionTypeEnum), nullable=False)
    transaction_status = db.Column(db.Enum(TransactionStatusEnum), default=TransactionStatusEnum.pending)

    cinema = db.relationship("Cinema", backref=backref("transactions", uselist=True))
    author = db.relationship("User", backref=backref("transactions", uselist=True))

    payment_url = db.Column(db.String, nullable=True)

    __reservation = db.relationship('Reservation', secondary='reservation_transaction_dict', cascade="all, delete",
                                    uselist=False)
    __certificate = db.relationship('Certificate', secondary='certificate_transaction_dict', cascade="all, delete",
                                    uselist=False)

    def __init__(cls, **kwargs):
        super().__init__(**kwargs)

        if not cls.id:
            cls.id = Transaction.generate_id()

    @property
    def is_refund_available(self):
        if self.__reservation:
            transaction_local_date = convert_tz(self.created_at, self.cinema.city.timezone)
            transaction_shift_date = (transaction_local_date - timedelta(days=1)).date() \
                if transaction_local_date.time() < time(8) \
                else transaction_local_date.date()

            reservation_local_date = convert_tz(self.__reservation.date, self.cinema.city.timezone)
            reservation_shift_date = (reservation_local_date - timedelta(days=1)).date() \
                if (reservation_local_date + timedelta(hours=self.__reservation.duration)).time() < time(8) \
                else reservation_local_date.date()

            is_preorder = transaction_shift_date < reservation_shift_date

            if not is_preorder:
                return False

            return (reservation_shift_date - transaction_shift_date).days >= 2

        return False

    @staticmethod
    def generate_id():
        return shortuuid.ShortUUID().random(length=40)

    @staticmethod
    def to_json(transaction: "Transaction"):
        return {
            "id": transaction.id,
            "created_at": transaction.created_at.strftime("%d-%m-%Y %H:%M"),
            "sum": transaction.sum,
            "alias": transaction.alias,
            "description": transaction.description,
            "author": User.to_json(transaction.author),
            "transaction_type": transaction.transaction_type.value,
            "transaction_status": transaction.transaction_status.value,
            "related_reservation_id": transaction.__reservation.id if transaction.__reservation else None,
            "related_certificate_id": transaction.__certificate.ident if transaction.__certificate else None,
            "payment_url": transaction.payment_url,
            "is_refund_available": transaction.is_refund_available
        }
