from datetime import datetime, timedelta

from sqlalchemy import func

from models import Reservation, ReservationStatusEnum, Room


def check_the_taking(date: datetime, room: Room, duration: float, reservation_id=None):
    """Проверяет занят ли зал"""
    reservation_id = int(reservation_id) if type(reservation_id) == str else reservation_id

    reservations = Reservation \
        .query \
        .filter(func.date(Reservation.date).in_([date.date() - timedelta(days=1), date.date(), date.date() + timedelta(days=1)])) \
        .filter(Reservation.room == room) \
        .all()

    new_reservation_end_date = date + timedelta(hours=duration)

    for reservation in reservations:
        if reservation.status == ReservationStatusEnum.canceled:
            continue

        if reservation_id is not None and reservation.id == reservation_id:
            continue

        reservation_end_date = reservation.date + timedelta(hours=reservation.duration)

        if date == reservation.date:
            return True

        if date < reservation.date <= new_reservation_end_date:
            return True

        if reservation.date < date <= reservation_end_date:
            return True

    return False
