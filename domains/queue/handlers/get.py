from datetime import datetime, timedelta

from flask import request, jsonify, json

from utils.filter_items_from_another_shift import filter_items_from_another_shift

from models import ReservationQueue, QueueStatusEnum, Room, Guest
from utils.inersection import intersection


def get_queue():
    room_id = int(request.args.get('room_id')) if request.args.get('room_id') else None
    date = datetime.strptime(request.args.get('date'), '%Y-%m-%d').date()
    cinema_id = int(request.args.get('cinema_id'))

    if not date:
        return {"message": "Не все данные"}, 400

    queue = ReservationQueue.query.filter(ReservationQueue.date.in_([date, date + timedelta(days=1)])).all()

    # Я хз как через алхимию такой фильтр сделать, фильтрую силами питона
    if not room_id:
        queue = filter(lambda item: cinema_id in set([room.cinema_id for room in item.rooms]), queue)
    else:
        queue = filter(lambda item: int(room_id) in [room.id for room in item.rooms], queue)

    queue = filter(lambda item: filter_items_from_another_shift(item, date), queue)

    return jsonify([ReservationQueue.to_json(queue_item) for queue_item in queue]), 200

def search_in_queue():
    statuses: list[QueueStatusEnum] = request.args.get('status')
    rooms: list[Room] = request.args.get('room')
    ids: list[str] = request.args.get('ids')
    telephones: list[str] = request.args.get('telephones')
    start_date: str = request.args.get('start_date')
    end_date: str = request.args.get('end_date')
    has_another_reservation: list[bool] = request.args.get('has_another_reservation')

    queue_query = ReservationQueue.query.join(Guest)

    if statuses:
        statuses = [QueueStatusEnum[status] for status in json.loads(statuses)]
        queue_query = queue_query.filter(ReservationQueue.status.in_(statuses))

    if ids:
        ids = json.loads(ids)
        queue_query = queue_query.filter(ReservationQueue.id.in_(ids))

    if telephones:
        telephones = json.loads(telephones)
        queue_query = queue_query.filter(Guest.telephone.in_(telephones))

    if start_date:
        queue_query = queue_query.filter(ReservationQueue.date >= start_date)

    if end_date:
        queue_query = queue_query.filter(ReservationQueue.date <= end_date)

    if has_another_reservation:
        has_another_reservation = json.loads(has_another_reservation)
        queue_query = queue_query.filter(ReservationQueue.has_another_reservation.in_(has_another_reservation))

    queue: list['ReservationQueue'] = queue_query.all()

    if rooms:
        rooms_id = [room["id"] for room in json.loads(rooms)]
        queue = list(filter(lambda i: intersection([room.id for room in i.rooms], rooms_id), queue))

    return jsonify([ReservationQueue.to_json(item) for item in queue]), 200
