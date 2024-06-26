import json

from sqlalchemy import func

from db import db
from models.abstract import AbstractBaseModel


class TransactionChangesLog(AbstractBaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    transaction_id = db.Column(db.Integer, db.ForeignKey("transaction.id", name="transaction_id"))
    created_at = db.Column(db.DateTime, default=func.localtimestamp())
    author = db.Column(db.String)

    old = db.Column(db.Text)
    new = db.Column(db.Text)

    @staticmethod
    def to_json(self):
        return {
            "id": self.id,
            "created_at": self.created_at.strftime('%Y-%m-%dT%H:%M'),
            "author": self.author,
            "old": json.loads(self.old),
            "new": json.loads(self.new)
        }
