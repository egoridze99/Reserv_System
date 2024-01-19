from sqlalchemy import func

from db import db
from models.abstract import AbstractBaseModel
from models.dictionaries import queue_room, queue_logs
from models.entities.Guest import Guest
from models.entities.Room import Room
from models.entities.User import User
from models.enums.QueueStatusEnum import QueueStatusEnum


class ReservationQueue(AbstractBaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=True)
    duration = db.Column(db.Integer, nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey("guest.id", name="contact_id"))
    guests_count = db.Column(db.Integer, nullable=False)
    has_another_reservation = db.Column(db.Boolean, default=False, nullable=False)
    status = db.Column(db.Enum(QueueStatusEnum), default=QueueStatusEnum.active)
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=func.now())
    author_id = db.Column(db.Integer, db.ForeignKey("user.id", name="author_id"))

    rooms = db.relationship('Room', secondary=queue_room)
    view_logs = db.relationship('ReservationQueueViewLog', secondary=queue_logs)

    @staticmethod
    def to_json(reservation: 'ReservationQueue'):
        return {
            'id': reservation.id,
            'date': reservation.date,
            'start_time': str(reservation.start_time)[:-3],
            'end_time': str(reservation.end_time)[:-3] if reservation.end_time else None,
            'has_another_reservation': reservation.has_another_reservation,
            'duration': reservation.duration,
            'guests_count': reservation.guests_count,
            'status': reservation.status.value,
            'note': reservation.note,
            'created_at': reservation.created_at.strftime("%d-%m-%Y %H:%M"),
            'author': User.to_json(reservation.author),
            'rooms': [Room.to_json(room) for room in reservation.rooms],
            'contact': Guest.to_json(reservation.contact),
            'view_by': [{"reservation_id": log.reservation.id,
                         "user": User.to_json(log.user),
                         "created_at": str(log.created_at)[:8:]
                         } for log in reservation.view_logs]
        }
