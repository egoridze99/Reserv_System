from db import db
from models.abstract import AbstractBaseModel


class Checkout(AbstractBaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sum = db.Column(db.Integer, nullable=True)
    description = db.Column(db.String(500), nullable=False)

    @staticmethod
    def to_json(checkout: 'Checkout'):
        return {
            "id": checkout.id,
            "sum": checkout.sum,
            "note": checkout.description
        }