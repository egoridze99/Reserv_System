from sqlalchemy import func

from db import db
from models import Room, Cinema, Reservation, City, ReservationStatusEnum
from utils.parse_date import parse_shift_range


def get_duration_query(until, till):
    min_date, max_date = parse_shift_range(until, till)

    durations = db.session.query(
        Cinema.id.label("cinema_id"),
        Room.id.label('room_id'),
        func.sum(Reservation.duration).label("sum")) \
        .join(Room, Reservation.room_id == Room.id) \
        .join(Cinema, Room.cinema_id == Cinema.id) \
        .join(City, Cinema.city_id == City.id) \
        .filter(func.datetime(Reservation.end_date, City.timezone).between(min_date, max_date)) \
        .filter(Reservation.status == ReservationStatusEnum.finished) \
        .group_by(Reservation.room_id).all()

    result = {}

    for row in durations:
        cinema = result.setdefault(row.cinema_id, {"cinema_id": row.cinema_id, "sum": 0, "rooms": {}})
        cinema["sum"] += row.sum
        cinema["rooms"][row.room_id] = row.sum

    return result
