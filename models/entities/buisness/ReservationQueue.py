from sqlalchemy import func

from db import db
from models.abstract import AbstractBaseModel
from models.dictionaries import queue_room, queue_logs
from models.entities.buisness import Guest
from models.entities.buisness.Room import Room
from models.entities.buisness.User import User
from models.enums.QueueStatusEnum import QueueStatusEnum


class ReservationQueue(AbstractBaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    duration = db.Column(db.Integer, nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey("guest.id", name="contact_id"))
    guests_count = db.Column(db.Integer, nullable=False)
    has_another_reservation = db.Column(db.Boolean, default=False, nullable=False)
    status = db.Column(db.Enum(QueueStatusEnum), default=QueueStatusEnum.active)
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=func.localtimestamp())
    author_id = db.Column(db.Integer, db.ForeignKey("user.id", name="author_id"))

    rooms = db.relationship('Room', secondary=queue_room)
    view_logs = db.relationship('ReservationQueueViewLog', secondary=queue_logs)

    @staticmethod
    def to_json(reservation: 'ReservationQueue'):
        return {
            'id': reservation.id,
            'start_date': reservation.start_date.strftime('%Y-%m-%dT%H:%M'),
            'end_date': reservation.end_date.strftime('%Y-%m-%dT%H:%M') if reservation.end_date else None,
            'has_another_reservation': reservation.has_another_reservation,
            'duration': reservation.duration,
            'guests_count': reservation.guests_count,
            'status': reservation.status.value,
            'note': reservation.note,
            'created_at': reservation.created_at.strftime('%Y-%m-%dT%H:%M'),
            'author': User.to_json(reservation.author),
            'rooms': [Room.to_json(room) for room in reservation.rooms],
            'contact': Guest.to_json(reservation.contact),
            'view_by': [{"reservation_id": log.reservation.id,
                         "user": User.to_json(log.user),
                         "created_at": log.created_at.strftime('%Y-%m-%dT%H:%M')
                         } for log in reservation.view_logs]
        }
