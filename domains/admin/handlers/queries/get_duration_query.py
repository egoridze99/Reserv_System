from datetime import datetime, time, timedelta
from functools import reduce

from sqlalchemy import func, cast, String

from db import db
from models import Room, Cinema, Reservation, City, ReservationStatusEnum


def get_duration_query(until, till):
    db_session = db.session

    until = datetime.strptime(until, "%Y-%m-%d")
    if till:
        till = datetime.strptime(till, "%Y-%m-%d")

    min_date = datetime.combine(until, time(8))
    max_date = datetime.combine(till + timedelta(days=1), time(8))

    durations = db_session.query(
        Cinema.id.label("cinema_id"),
        Room.id.label('room_id'),
        func.sum(Reservation.duration).label("sum")) \
        .join(Room, Reservation.room_id == Room.id) \
        .join(Cinema, Room.cinema_id == Cinema.id) \
        .join(City, Cinema.city_id == City.id) \
        .filter(func.datetime(func.datetime(Reservation.date, '+' + cast(Reservation.duration, String) + ' hours'),
                              City.timezone).between(min_date, max_date)) \
        .filter(Reservation.status == ReservationStatusEnum.finished) \
        .group_by(Reservation.room_id).all()

    durations_grouped_by_cinema_id = {}

    for row in durations:
        if row.cinema_id not in durations_grouped_by_cinema_id:
            durations_grouped_by_cinema_id[row.cinema_id] = []

        durations_grouped_by_cinema_id[row.cinema_id].append(row)

    result = {}

    for cinema_id, rooms in durations_grouped_by_cinema_id.items():
        result[cinema_id] = {
            "cinema_id": cinema_id,
            "sum": sum([room.sum for room in rooms]),
        }

        for room in rooms:
            if 'rooms' not in result[cinema_id]:
                result[cinema_id]['rooms'] = {}

            result[cinema_id]['rooms'][room.room_id] = room.sum

    return result
