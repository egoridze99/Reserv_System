from datetime import datetime, timedelta, time

from flask import request

from constants.time import MOSCOW_OFFSET
from db import db
from models import Guest, ReservationQueue, Room, QueueStatusEnum
from utils.convert_tz import convert_tz
from utils.parse_json import parse_json
from utils.reduce_city_from_rooms import reduce_city_from_rooms


def edit_queue_item(id: int):
    data = parse_json(request.data)

    queue_item: 'ReservationQueue' = ReservationQueue.query.filter_by(id=id).first()

    if queue_item is None:
        return {"msg": "Элемента с таким id не найдено в очереди"}, 404

    rooms = Room.query.filter(Room.id.in_(data['rooms'])).all()
    city = reduce_city_from_rooms(rooms)
    contact = Guest.query.filter(Guest.id == data['contact']).first()

    if contact is None:
        return {"msg": "Пользователь не найден"}, 400

    date = datetime.strptime(f"{data['date']}", '%Y-%m-%d')
    start_time = datetime.strptime(data['start_time'], '%H:%M').time()
    end_time = datetime.strptime(data["end_time"], '%H:%M').time() if data["end_time"] else None

    start_date = convert_tz(datetime.combine(date, start_time), city.timezone or MOSCOW_OFFSET, True)
    end_date = None

    if end_time:
        if start_time > end_time > time(8):
            return {"msg": "Неверный временной диапазон"}, 400

        end_date = date + timedelta(days=1) if end_time < start_time else date
        end_date = convert_tz(datetime.combine(end_date, end_time), city.timezone or MOSCOW_OFFSET, True)

    queue_item.start_date = start_date
    queue_item.end_date = end_date
    queue_item.duration = data["duration"]
    queue_item.guests_count = data["guests_count"]
    queue_item.has_another_reservation = data["has_another_reservation"]
    queue_item.note = data["note"]
    queue_item.contact = contact
    queue_item.rooms = rooms
    queue_item.status = QueueStatusEnum[data["status"]]

    db.session.add(queue_item)

    try:
        db.session.commit()
        return {"msg": "ok"}, 200
    except:
        return {"msg": "Произошла ошибка при сохранении"}, 400


def close_queue_item(id: int):
    queue_item: 'ReservationQueue' = ReservationQueue.query.filter_by(id=id).first()
    if queue_item is None:
        return {"msg": "Элемента с таким id не найдено в очереди"}, 404

    if queue_item.status not in (QueueStatusEnum.active, QueueStatusEnum.waiting):
        return {"msg": "Статус элемента в очереди - неактивен"}, 400

    queue_item.status = QueueStatusEnum.reserved

    try:
        db.session.add(queue_item)
        db.session.commit()
        return {"msg": "ok"}, 200
    except:
        return {"msg": "Произошла непредвиденная ошибка"}, 400
