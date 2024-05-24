from sqlalchemy import func, text

from db import db
from models import TransactionStatusEnum, Room, Cinema, Reservation, City, ReservationStatusEnum


def get_duration_query(area, until, till):
    db_session = db.session

    duration = db_session.query(
        (Room if area == 'room' else Cinema).name.label('area'),
        func.sum(Reservation.duration).label('sum')) \
        .join(Room, Reservation.room_id == Room.id) \
        .join(Cinema, Room.cinema_id == Cinema.id) \
        .join(City, Cinema.city_id == City.id) \
        .filter(text(
        "date(get_shift_date(reservation.date, city.timezone, reservation.duration)) between date(:untill) and date(:till)")).params(
        untill=until, till=till) \
        .filter(Reservation.status == ReservationStatusEnum.finished) \
        .group_by((Room if area == 'room' else Cinema).id).all()

    return [{"area": row.area, "sum": row.sum} for row in duration]
