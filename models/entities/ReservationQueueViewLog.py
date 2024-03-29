from datetime import datetime

from sqlalchemy import func

from db import db
from models.abstract import AbstractBaseModel


class ReservationQueueViewLog(AbstractBaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    reservation_id = db.Column(db.Integer, db.ForeignKey("reservation.id", name="reservation_id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", name="user_id"))
    created_at = db.Column(db.DateTime, default=func.datetime(func.localtimestamp()))

    reservation = db.relationship("Reservation")
    user = db.relationship("User")
