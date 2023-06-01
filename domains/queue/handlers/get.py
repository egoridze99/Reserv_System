from datetime import datetime, timedelta

from flask import request, jsonify

from utils.filter_items_from_another_shift import filter_items_from_another_shift

from models import ReservationQueue


def get_queue():
    room_id = int(request.args.get('room_id'))
    date = datetime.strptime(request.args.get('date'), '%Y-%m-%d').date()
    cinema_id = int(request.args.get('cinema_id'))

    if not room_id or not date:
        return {"message": "Не все данные"}, 400

    queue = ReservationQueue.query.filter(ReservationQueue.date.in_([date, date + timedelta(days=1)])).all()

    # Я хз как через алхимию такой фильтр сделать, фильтрую силами питона
    if room_id == -1:
        queue = filter(lambda item: cinema_id in set([room.cinema_id for room in item.rooms]), queue)
    else:
        queue = filter(lambda item: int(room_id) in [room.id for room in item.rooms], queue)

    queue = filter(lambda item: filter_items_from_another_shift(item, date), queue)

    return jsonify([ReservationQueue.to_json(queue_item) for queue_item in queue]), 200
