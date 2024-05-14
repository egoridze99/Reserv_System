import shortuuid
from sqlalchemy import func
from sqlalchemy.orm import backref

from db import db
from models.abstract import AbstractBaseModel
from models.enums import TransactionStatusEnum, TransactionTypeEnum


class Transaction(AbstractBaseModel):
    __tablename__ = 'transaction'

    id = db.Column(db.String, primary_key=True)
    created_at = db.Column(db.DateTime, default=func.localtimestamp(), nullable=False)

    sum = db.Column(db.Integer, nullable=False)
    alias = db.Column(db.String)
    description = db.Column(db.String)

    cinema_id = db.Column(db.Integer, db.ForeignKey('cinema.id'), nullable=False)

    transaction_type = db.Column(db.Enum(TransactionTypeEnum), nullable=False)
    transaction_status = db.Column(db.Enum(TransactionStatusEnum), default=TransactionStatusEnum.pending)

    cinema = db.relationship("Cinema", backref=backref("transactions", uselist=True))

    def __init__(cls, **kwargs):
        super().__init__(**kwargs)
        cls.id = shortuuid.ShortUUID().random(length=32)
