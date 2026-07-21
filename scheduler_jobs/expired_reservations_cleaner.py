from datetime import datetime, timedelta

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from models import Reservation, ReservationStatusEnum, CertificateStatusEnum


def expired_reservations_cleaner(app: 'Flask', db: SQLAlchemy):
    with app.app_context():
        finished_reservations = Reservation \
            .query \
            .filter(Reservation.end_date <= datetime.now() - timedelta(minutes=30)) \
            .filter(Reservation.status.in_(
            [ReservationStatusEnum.progress, ReservationStatusEnum.waiting, ReservationStatusEnum.not_allowed])) \
            .all()

        for reservation in finished_reservations:
            reservation.status = ReservationStatusEnum.finished

            if reservation.certificate:
                reservation.certificate.status = CertificateStatusEnum.redeemed

            db.session.add(reservation)

        db.session.commit()
