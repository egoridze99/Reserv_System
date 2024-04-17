from datetime import datetime, time, timedelta

from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from db import db
from models import User, Guest, Room, ReservationQueue
from utils.parse_json import parse_json


def create_reservation_in_queue():
    """Создать новый элемент в очереди"""

    data = parse_json(request.data)
    author = User.query.filter(User.id == get_jwt_identity()["id"]).first()
    guest = Guest.query.filter(Guest.id == data["contact"]).first()
    rooms = Room.query.filter(Room.id.in_(data['rooms'])).all()

    if guest is None:
        return {"msg", "Пользователь не найден"}, 400

    date = datetime.strptime(data['date'], '%Y-%m-%d').date()

    start_time = datetime.strptime(data['start_time'], '%H:%M').time()
    end_time = datetime.strptime(data["end_time"], '%H:%M').time() if data["end_time"] else None

    start_date = datetime.combine(date, start_time)
    end_date = None

    if end_time:
        if start_time > end_time > time(8):
            return {"msg": "Неверный временной диапазон"}, 400

        end_date = date + timedelta(days=1) if end_time < start_time else date
        end_date = datetime.combine(end_date, end_time)

    queue_item = ReservationQueue(
        start_date=start_date,
        end_date=end_date,
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
