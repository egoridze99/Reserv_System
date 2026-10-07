from db import db
from models.abstract import ChangeLogMixin


class GuestChangesLogs(ChangeLogMixin, db.Model):
    guest_id = db.Column(db.Integer, db.ForeignKey("guest.id", name="guest_id"), index=True)
