from sqlalchemy import func

from db import db
from models.entities.buisness import Guest
from models.enums.UserStatusEnum import UserStatusEnum
from models.abstract import AbstractBaseModel
from models.entities.buisness.Certificate import Certificate
from models.enums.ReservationStatusEnum import ReservationStatusEnum


class Reservation(AbstractBaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    count = db.Column(db.Integer)  # Кол-во гостей
    room_id = db.Column(db.Integer, db.ForeignKey('room.id', name="room_id"))
    guest_id = db.Column(db.Integer, db.ForeignKey('guest.id', name="guest_id"))
    film = db.Column(db.String(170))
    note = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id', name="author_id"))
    created_at = db.Column(db.DateTime, default=func.localtimestamp())
    certificate_id = db.Column(db.Integer, db.ForeignKey("certificate.id", name="certificate_id"), unique=True)
    status = db.Column(db.Enum(ReservationStatusEnum), default=ReservationStatusEnum.not_allowed, nullable=False)
    sum_rent = db.Column(db.Integer, default=0)

    transactions = db.relationship('Transaction', secondary='reservation_transaction_dict', cascade="all, delete")

    @staticmethod
    def to_json(reservation: 'Reservation'):
        return {
            'id': reservation.id,
            'date': reservation.date.strftime('%Y-%m-%dT%H:%M'),
            'room': {"id": reservation.room.id, "name": reservation.room.name},
            'duration': reservation.duration,
            'count': reservation.count,
            'film': reservation.film,
            'author': {"fullname": f"{reservation.author.name} {reservation.author.surname}" \
                if reservation.author is not None else "Кривой юзер",
                       "status": reservation.author.status.name \
                           if reservation.author is not None else UserStatusEnum.deprecated.name},
            'note': reservation.note,
            'status': reservation.status.name,
            'rent': reservation.sum_rent,
            'created_at': reservation.created_at.strftime(
                '%Y-%m-%dT%H:%M') if reservation.created_at is not None else None,
            "certificate": Certificate.to_json(reservation.certificate) if reservation.certificate else None,
            'guest': Guest.to_json(reservation.guest),
        }
