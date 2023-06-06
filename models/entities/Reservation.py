from db import db
from models.enums.UserStatusEnum import UserStatusEnum
from models.abstract import AbstractBaseModel
from models.dictionaries import checkout_reservation
from models.entities.Certificate import Certificate
from models.entities.Checkout import Checkout
from models.enums.ReservationStatusEnum import ReservationStatusEnum


class Reservation(AbstractBaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    count = db.Column(db.Integer)  # Кол-во гостей
    room_id = db.Column(db.Integer, db.ForeignKey('room.id', name="room_id"))
    guest_id = db.Column(db.Integer, db.ForeignKey('guest.id', name="guest_id"))
    film = db.Column(db.String(170))
    note = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id', name="author_id"))
    created_at = db.Column(db.String(10))
    certificate_id = db.Column(db.Integer, db.ForeignKey("certificate.id", name="certificate_id"), unique=True)
    status = db.Column(db.Enum(ReservationStatusEnum), default=ReservationStatusEnum.not_allowed, nullable=False)
    sum_rent = db.Column(db.Integer, default=0)
    card = db.Column(db.Integer, default=0)
    cash = db.Column(db.Integer, default=0)

    checkout = db.relationship('Checkout', secondary=checkout_reservation)

    @staticmethod
    def to_json(reservation: 'Reservation'):
        return {
            'id': reservation.id,
            'date': reservation.date,
            'room': {"id": reservation.room.id, "name": reservation.room.name},
            'time': str(reservation.time)[:-3],
            'duration': reservation.duration,
            'count': reservation.count,
            'film': reservation.film,
            'author': {"fullname": f"{reservation.author.name} {reservation.author.surname}" \
                if reservation.author is not None else "Кривой юзер",
                       "status": reservation.author.status.name \
                if reservation.author is not None else UserStatusEnum.deprecated.name},
            'note': reservation.note,
            'status': reservation.status.name,
            'card': reservation.card,
            'cash': reservation.cash,
            'rent': reservation.sum_rent,
            'created_at': reservation.created_at,
            "certificate": Certificate.to_json(reservation.certificate) if reservation.certificate else None,
            'guest': {
                "name": reservation.guest.name,
                "tel": reservation.guest.telephone
            },
            'checkouts': [Checkout.to_json(checkout) for checkout in reservation.checkout]
        }

    def __str__(self):
        return """
            <
            id = {}
            Резерв дата = {}  время = {}  продолжительность = {}
            количество гостей = {} 
            зал = {} 
            гость = {}
            фильм = {} 
            статус = {}
            по карте = {} 
            наличка = {}
            >
        """.format(self.id, self.date, self.time, self.duration, self.count, self.room, self.guest,
                   self.film, self.status, self.card,
                   self.cash)
