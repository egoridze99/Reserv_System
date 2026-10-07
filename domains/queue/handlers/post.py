from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from db import db
from domains.queue.handlers.utils import compute_queue_dates
from models import User, Guest, Room, ReservationQueue
from utils.reduce_city_from_rooms import reduce_city_from_rooms


def create_reservation_in_queue():
    """Создать новый элемент в очереди"""

    data = request.get_json(force=True)
    author = User.query.filter(User.id == get_jwt_identity()["id"]).first()
    guest = Guest.query.filter(Guest.id == data["contact"]).first()
    rooms = Room.query.filter(Room.id.in_(data['rooms'])).all()
    city = reduce_city_from_rooms(rooms)

    if guest is None:
        return {"msg", "Пользователь не найден"}, 400

    dates = compute_queue_dates(data, city.timezone)

    if dates is None:
        return {"msg": "Неверный временной диапазон"}, 400

    queue_item = ReservationQueue(
        **dates,
        duration=data['duration'],
        guests_count=data['guests_count'],
        has_another_reservation=data['has_another_reservation'],
        note=data['note'],
        author=author,
        contact=guest,
        rooms=rooms
    )

    db.session.add(queue_item)
    db.session.commit()

    return jsonify(ReservationQueue.to_json(queue_item)), 201
