import json

from sqlalchemy import func

from db import db
from models.abstract import AbstractBaseModel
from utils.convert_tz import convert_tz


class UpdateLogs(AbstractBaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reservation_id = db.Column(db.Integer, db.ForeignKey("reservation.id", name="reservation_id"))
    created_at = db.Column(db.DateTime, default=func.localtimestamp())
    author = db.Column(db.String)

    old = db.Column(db.Text)
    new = db.Column(db.Text)

    @staticmethod
    def to_json(log, tz):
        return {
            "id": log.id,
            "created_at": convert_tz(log.created_at, tz, False).strftime('%Y-%m-%dT%H:%M'),
            "author": log.author,
            "old": json.loads(log.old),
            "new": json.loads(log.new)
        }
