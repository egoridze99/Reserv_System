from db import db
from models.abstract import ChangeLogMixin


class TransactionChangesLog(ChangeLogMixin, db.Model):
    transaction_id = db.Column(db.Integer, db.ForeignKey("transaction.id", name="transaction_id"), index=True)
