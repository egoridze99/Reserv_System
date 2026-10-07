from db import db
from models.abstract import ChangeLogMixin


class UpdateLogs(ChangeLogMixin, db.Model):
    reservation_id = db.Column(db.Integer, db.ForeignKey("reservation.id", name="reservation_id"), index=True)
