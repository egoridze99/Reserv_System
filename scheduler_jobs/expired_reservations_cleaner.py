from datetime import datetime, timedelta

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

from models import Reservation, ReservationStatusEnum
from db import db


def expired_reservations_cleaner(app: 'Flask', db: SQLAlchemy):
    with (((((app.app_context()))))):
        expired_reservations = Reservation \
            .query \
            .filter(func.date(Reservation.date) <= (datetime.now() - timedelta(days=1)).date()).all() \
            .filter(Reservation.status.in_([ReservationStatusEnum.progress, ReservationStatusEnum.waiting])) \
            .all()

        for reservation in expired_reservations:
            reservation.status = ReservationStatusEnum.finished
            db.session.add(reservation)

        db.session.commit()
