from datetime import datetime, timedelta

from apscheduler.schedulers.blocking import BlockingScheduler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from db import db
from models import ReservationQueue, QueueStatusEnum


class Scheduler:
    def __init__(self, scheduler: 'BlockingScheduler', db: 'SQLAlchemy', app: 'Flask'):
        self.scheduler = scheduler
        self.db = db
        self.app = app

    def start(self):
        self.scheduler.start()

    def register_clear_expired_queue_items_timer(self):
        def job():
            with self.app.app_context():
                reservations = ReservationQueue.query\
                    .filter(ReservationQueue.date < (datetime.now() - timedelta(days=1)).date()) \
                    .filter(ReservationQueue.status.in_([QueueStatusEnum.active, QueueStatusEnum.waiting])) \
                    .all()

                for reservation in reservations:
                    reservation.status = QueueStatusEnum.expired
                    db.session.add(reservation)

                self.db.session.commit()

        self.scheduler.add_job(job, 'cron', day="*", month="*", hour="06", minute='30')
