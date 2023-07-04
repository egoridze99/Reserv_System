from datetime import datetime

from flask import request, abort

from db import db
from models import Guest, ReservationQueue, Room, QueueStatusEnum
from utils.parse_json import parse_json


def edit_queue_item(id: int):
    data = parse_json(request.data)

    queue_item: 'ReservationQueue' = ReservationQueue.query.filter_by(id=id).first()

    if queue_item is None:
        return {"msg": "Элемента с таким id не найдено в очереди"}, 404

    rooms = Room.query.filter(Room.id.in_(data['rooms'])).all()
    contact = Guest.query.filter(Guest.telephone == data['telephone']).first()
    if contact is None:
        contact = Guest(name=data['contact'], telephone=data['telephone'])
        db.session.add(contact)

    date = datetime.strptime(f"{data['date']}", '%Y-%m-%d')
    start_time = datetime.strptime(data['start_time'], '%H:%M').time()
    end_time = datetime.strptime(data["end_time"], '%H:%M').time() if data["end_time"] else None

    queue_item.date = date
    queue_item.start_time = start_time
    queue_item.end_time = end_time
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
