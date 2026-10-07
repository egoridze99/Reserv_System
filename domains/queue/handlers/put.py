from flask import request

from db import db
from domains.queue.handlers.utils import compute_queue_dates
from models import Guest, ReservationQueue, Room, QueueStatusEnum
from utils.reduce_city_from_rooms import reduce_city_from_rooms


def edit_queue_item(id: int):
    data = request.get_json(force=True)

    queue_item: 'ReservationQueue' = ReservationQueue.query.filter_by(id=id).first()

    if queue_item is None:
        return {"msg": "Элемента с таким id не найдено в очереди"}, 404

    rooms = Room.query.filter(Room.id.in_(data['rooms'])).all()
    city = reduce_city_from_rooms(rooms)
    contact = Guest.query.filter(Guest.id == data['contact']).first()

    if contact is None:
        return {"msg": "Пользователь не найден"}, 400

    dates = compute_queue_dates(data, city.timezone)

    if dates is None:
        return {"msg": "Неверный временной диапазон"}, 400

    for field, value in dates.items():
        setattr(queue_item, field, value)

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
