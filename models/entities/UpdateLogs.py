import json

from db import db
from models.abstract import AbstractBaseModel


class UpdateLogs(AbstractBaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reservation_id = db.Column(db.Integer, db.ForeignKey("reservation.id", name="reservation_id"))
    created_at = db.Column(db.String)
    author = db.Column(db.String)

    old = db.Column(db.Text)
    new = db.Column(db.Text)

    @staticmethod
    def to_json(self):
        return {
            "id": self.id,
            "created_at": self.created_at,
            "author": self.author,
            "old": json.loads(self.old),
            "new": json.loads(self.new)
        }