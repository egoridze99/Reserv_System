from datetime import datetime, timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from db import db
from models import ReservationQueue, QueueStatusEnum


def expired_queue_item_cleaner(app: 'Flask', db: SQLAlchemy):
    with app.app_context():
        reservations = ReservationQueue.query \
            .filter(ReservationQueue.date <= (datetime.now() - timedelta(days=1)).date()) \
            .filter(ReservationQueue.status.in_([QueueStatusEnum.active, QueueStatusEnum.waiting])) \
            .all()
        for reservation in reservations:
            reservation.status = QueueStatusEnum.expired
            db.session.add(reservation)

        db.session.commit()
