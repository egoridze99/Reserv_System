import shortuuid
from sqlalchemy import func
from sqlalchemy.orm import backref

from db import db
from models.entities.buisness.User import User
from models.enums import TransactionStatusEnum, TransactionTypeEnum


class Transaction(db.Model):
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
        # Возвраты отключены. Прежнее правило (предзаказ, оплаченный за 2+ смены до резерва) — в истории git
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
