from datetime import datetime, timedelta, time

from flask import request, jsonify, json
from sqlalchemy import func, String, Integer, text
from sqlalchemy.orm import aliased
from sqlalchemy.sql.elements import Cast

from db import db
from models import ReservationQueue, QueueStatusEnum, Room, Guest, Cinema, City
from models.dictionaries import queue_room
from utils.inersection import intersection


def get_queue():
    room_id = int(request.args.get('room_id')) if request.args.get('room_id') else None
    date = datetime.strptime(request.args.get('date'), '%Y-%m-%d').date()
    cinema_id = int(request.args.get('cinema_id'))

    if not date:
        return {"message": "Не все данные"}, 400

    queue = ReservationQueue \
        .query \
        .join(queue_room) \
        .join(Room) \
        .join(Cinema) \
        .join(City) \
        .filter(
        (
                (func.date(ReservationQueue.start_date, func.substr(City.timezone, 0, 4) + " hours") == date) & (
                func.datetime(
                    ReservationQueue.start_date,
                    "+" + Cast(ReservationQueue.duration + Cast(func.substr(City.timezone, 0, 4), Integer),
                               String) + " hours"
                ) > datetime.combine(date, time(8)))) |
        (func.datetime(
            func.IIF(
                ReservationQueue.end_date,
                ReservationQueue.end_date,
                ReservationQueue.start_date
            ),
            "+" + Cast(ReservationQueue.duration + Cast(func.substr(City.timezone, 0, 4), Integer),
                       String) + " hours"
        ) <= datetime.combine(date + timedelta(days=1), time(8))) &
        (date + timedelta(days=1) == func.date(
            func.IIF(
                ReservationQueue.end_date,
                ReservationQueue.end_date,
                ReservationQueue.start_date
            ), func.substr(City.timezone, 0, 4) + " hours")
         )
    )

    # Я хз как через алхимию такой фильтр сделать, фильтрую силами питона
    if not room_id:
        queue = queue.filter(Room.cinema_id == cinema_id)
    else:
        queue = filter(lambda item: int(room_id) in [room.id for room in item.rooms], queue)

    return jsonify([ReservationQueue.to_json(queue_item) for queue_item in queue]), 200


def search_in_queue():
    statuses: list[QueueStatusEnum] = request.args.get('status')
    rooms: list[Room] = request.args.get('room')
    ids: list[int] = request.args.get('ids')
    telephones: list[str] = request.args.get('telephones')
    start_date: str = request.args.get('start_date')
    end_date: str = request.args.get('end_date')
    has_another_reservation: list[bool] = request.args.get('has_another_reservation')

    ReservationQueueAlias = aliased(ReservationQueue, name='rq_alias')
    queue_query = db.session.query(ReservationQueueAlias).join(Guest)

    if statuses:
        statuses = [QueueStatusEnum[status] for status in json.loads(statuses)]
        queue_query = queue_query.filter(ReservationQueueAlias.status.in_(statuses))

    if ids:
        ids = list(map(int, json.loads(ids)))
        queue_query = queue_query.filter(ReservationQueueAlias.id.in_(ids))

    if telephones:
        telephones = json.loads(telephones)
        queue_query = queue_query.filter(Guest.telephone.in_(telephones))

    subquery = """date(
                    get_shift_date(
                        rq_alias.start_date,
                        (select city.timezone from reservation_queue
                            join queue_room on reservation_queue.id = queue_room.queue_id
                            join room on queue_room.room_id = room.id
                            join cinema on cinema.id = room.cinema_id
                            join city on cinema.city_id = city.id
                        where reservation_queue.id = rq_alias.id
                        group by city.id
                        limit 1),
                        rq_alias.duration))"""

    if start_date:
        start_date_str = datetime.strptime(start_date, "%Y-%m-%d").date()
        queue_query = queue_query.filter(text(f"""{subquery} >= :start_date""")).params(start_date=start_date_str)

    if end_date:
        end_date_str = datetime.strptime(end_date, "%Y-%m-%d").date()
        queue_query = queue_query.filter(text(f"""{subquery} <= :end_date""")).params(end_date=end_date_str)

    if has_another_reservation:
        has_another_reservation = json.loads(has_another_reservation)
        queue_query = queue_query.filter(ReservationQueueAlias.has_another_reservation.in_(has_another_reservation))

    queue: list['ReservationQueue'] = queue_query.all()

    if rooms:
        rooms_id = json.loads(rooms)
        queue = list(filter(lambda i: intersection([room.id for room in i.rooms], rooms_id), queue))

    return jsonify([ReservationQueue.to_json(item) for item in queue]), 200
