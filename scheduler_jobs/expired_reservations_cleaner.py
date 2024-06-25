from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, cast, String

from models import Reservation, ReservationStatusEnum, CertificateStatusEnum


def expired_reservations_cleaner(app: 'Flask', db: SQLAlchemy):
    with app.app_context():
        finished_reservations = Reservation \
            .query \
            .filter(func.datetime(
            func.datetime(Reservation.date, '+' + cast(Reservation.duration, String) + ' hours',
                          '+30 minutes')) <= datetime.now()) \
            .filter(Reservation.status.in_(
            [ReservationStatusEnum.progress, ReservationStatusEnum.waiting, ReservationStatusEnum.not_allowed])) \
            .all()

        for reservation in finished_reservations:
            reservation.status = ReservationStatusEnum.finished

            if reservation.certificate:
                reservation.certificate.status = CertificateStatusEnum.redeemed

            db.session.add(reservation)

        db.session.commit()
