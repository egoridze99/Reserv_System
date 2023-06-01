from datetime import datetime, timedelta

from models import Reservation, ReservationStatusEnum


def check_the_taking(date: datetime.date, room: int, time: datetime.time, duration: float, reservation_id=None):
    """Проверяет занят ли зал"""

    reservations = Reservation\
        .query\
        .filter(Reservation.date.in_([date - timedelta(days=1), date]))\
        .filter(Reservation.room == room)\
        .all()

    new_reservation_start_date = datetime.combine(date, time)
    new_reservation_end_date = new_reservation_start_date + timedelta(hours=duration)

    for reservation in reservations:
        if reservation.status == ReservationStatusEnum.canceled:
            continue

        if reservation_id is not None and reservation.id == int(reservation_id):
            continue

        reservation_start_date = datetime.combine(reservation.date, reservation.time)
        reservation_end_date = reservation_start_date + timedelta(hours=reservation.duration)

        if new_reservation_start_date == reservation_start_date:
            return True

        if new_reservation_start_date < reservation_start_date <= new_reservation_end_date:
            return True

        if reservation_start_date < new_reservation_start_date <= reservation_end_date:
            return True

    return False
