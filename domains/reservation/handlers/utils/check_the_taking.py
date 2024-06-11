from datetime import datetime, timedelta

from sqlalchemy import func

from constants.time import MOSCOW_OFFSET
from models import Reservation, ReservationStatusEnum, Room
from utils.set_tz import set_tz


def check_the_taking(date: datetime, room: Room, duration: float, reservation_id=None):
    """Проверяет занят ли зал"""
    reservation_id = int(reservation_id) if type(reservation_id) == str else reservation_id

    reservations = Reservation \
        .query \
        .filter(func.date(Reservation.date).in_(
        [date.date() - timedelta(days=1), date.date(), date.date() + timedelta(days=1)])) \
        .filter(Reservation.room == room) \
        .all()

    new_reservation_end_date = date + timedelta(hours=duration)

    for reservation in reservations:
        if reservation.status == ReservationStatusEnum.canceled:
            continue

        if reservation_id is not None and reservation.id == reservation_id:
            continue

        reservation_date_with_tz = set_tz(reservation.date, MOSCOW_OFFSET)
        reservation_end_date = reservation_date_with_tz + timedelta(hours=reservation.duration)

        if date == reservation_date_with_tz:
            return True

        if date < reservation_date_with_tz <= new_reservation_end_date:
            return True

        if reservation_date_with_tz < date <= reservation_end_date:
            return True

    return False
