"""Переведет время в московское

Revision ID: 7e826343320d
Revises: 938d3c9182b0
Create Date: 2024-05-17 19:18:30.352497

"""
from datetime import timedelta, timezone

from alembic import op
from sqlalchemy import orm
from sqlalchemy.orm import object_session

from models import Reservation, ReservationQueue

# revision identifiers, used by Alembic.
revision = '7e826343320d'
down_revision = '938d3c9182b0'
branch_labels = None
depends_on = None


def upgrade():
    def update_reservations():
        session = None
        reservations = Reservation.query.all()

        for reservation in reservations:
            if not session:
                session = object_session(reservation)

            city = reservation.room.cinema.city
            moscow_offset = "+00:00"

            offset_hours, offset_minutes = map(int, city.timezone.split(':'))
            offset = timedelta(hours=offset_hours, minutes=offset_minutes)
            tz = timezone(offset)

            moscow_tz = timezone(
                timedelta(hours=int(moscow_offset[:3]), minutes=int(moscow_offset[4:])))

            reservation_date_with_timezone = reservation.date.replace(tzinfo=tz)
            reservation.date = reservation_date_with_timezone.astimezone(moscow_tz)

            session.add(reservation)

        session.commit()

    def update_queue():
        session = None
        queue_items = ReservationQueue.query.all()

        for item in queue_items:
            if not session:
                session = object_session(item)

            cinema = None
            for room in item.rooms:
                cinema = cinema or room.cinema

            city = cinema.city
            moscow_offset = "+00:00"

            offset_hours, offset_minutes = map(int, city.timezone.split(':'))
            offset = timedelta(hours=offset_hours, minutes=offset_minutes)
            tz = timezone(offset)

            moscow_tz = timezone(
                timedelta(hours=int(moscow_offset[:3]), minutes=int(moscow_offset[4:])))

            item_start_date_with_timezone = item.start_date.replace(tzinfo=tz)
            item.start_date = item_start_date_with_timezone.astimezone(moscow_tz)

            if item.end_date:
                item_end_date_with_timezone = item.end_date.replace(tzinfo=tz)
                item.end_date = item_end_date_with_timezone.astimezone(moscow_tz)

            session.add(item)

        session.commit()

    update_reservations()
    update_queue()


def downgrade():
    pass
