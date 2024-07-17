from datetime import datetime, timedelta, time
from typing import Optional, List

from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from constants.time import MOSCOW_OFFSET
from db import db
from domains.reservation.handlers.utils import check_not_payment, check_the_taking, \
    dump_reservation_to_update_log, search_available_items_from_queue
from models import EmployeeRoleEnum, Reservation, Room, Guest, Certificate, CertificateStatusEnum, \
    ReservationStatusEnum, UpdateLogs, User, ReservationQueue, ReservationQueueViewLog
from typings import UserJwtIdentity
from utils.convert_tz import convert_tz
from utils.is_date_in_last import is_date_in_last
from utils.parse_json import parse_json
from utils.set_tz import set_tz


def update_reservation(reservation_id: str):
    data = parse_json(request.data)
    identity: 'UserJwtIdentity' = get_jwt_identity()

    role = identity["role"]
    update_author = identity["name"]

    if EmployeeRoleEnum[role] == EmployeeRoleEnum.operator:
        return {"message": "У вас не хватает прав на это"}, 403

    reservation = Reservation.query.filter(Reservation.id == reservation_id).first()
    room = Room.query.filter(Room.id == data['room']).first()
    guest = Guest.query.filter(Guest.id == data['guest']).first()
    user = User.query.filter(User.id == identity["id"]).first()

    new_date = convert_tz(datetime.strptime(f"{data['date']} {data['time']}", "%Y-%m-%d %H:%M"),
                          room.cinema.city.timezone,
                          True)

    if is_date_in_last(new_date) and role != EmployeeRoleEnum.root.value and set_tz(reservation.date,
                                                                                    MOSCOW_OFFSET) != new_date:
        return {"msg": "Дата уже прошла"}, 400

    if is_date_in_last(
            set_tz(reservation.date, MOSCOW_OFFSET) + timedelta(hours=data['duration'])) and \
            reservation.duration > data["duration"]:
        return {"msg": "Вы пытаетесь уменьшить продолжительность резерва"}, 400

    certificate = None
    certificate_ident = data["certificate_ident"]
    if certificate_ident:
        certificate: Optional['Certificate'] = Certificate.query.filter(Certificate.ident == certificate_ident).first()

        if not certificate:
            return jsonify({"msg": "Сертификат не найден"}), 404

    if certificate and certificate != reservation.certificate:
        if certificate.status != CertificateStatusEnum.active:
            return {"msg": "Вы пытаетесь добавить погашенный сертификат"}, 400

    if reservation.certificate and ReservationStatusEnum[data["status"]] == ReservationStatusEnum.canceled:
        reservation.certificate_id = None

    if reservation.status == ReservationStatusEnum.finished:
        if role != EmployeeRoleEnum.root.name:
            return {"msg": "Нельзя изменять завершенные сеансы!"}, 400

        if check_not_payment(role, reservation, data["rent"], certificate):
            return {"msg": "Клиент не заплатил!"}, 400

    if reservation.date.date() < (datetime.now() - timedelta(days=1)).date() \
            and data['status'] != ReservationStatusEnum.finished.name \
            and role != EmployeeRoleEnum.root.name:
        return {"msg": "Вы пытаетесь отредактировать старый сеанс!"}, 400

    reservation_end_date = reservation.date + timedelta(hours=reservation.duration)
    if reservation_end_date.date() > datetime.now().date():
        def check_other_constraints(data, role):
            return ReservationStatusEnum[data['status']] == ReservationStatusEnum.finished \
                and EmployeeRoleEnum[role] != EmployeeRoleEnum.root

        if reservation_end_date.date() == (datetime.now() + timedelta(days=1)).date():
            max_end_time = set_tz(datetime.combine((datetime.now() + timedelta(days=1)).date(), time(8)),
                                  reservation.room.cinema.city.timezone).time()

            if reservation_end_date.time() > max_end_time and check_other_constraints(data, role):
                return {"msg": "Как может завершиться сеанс в будещем?)"}, 400
        else:
            if check_other_constraints(data, role):
                return {"msg": "Как может завершиться сеанс в будещем?)"}, 400

    if check_the_taking(new_date, room, float(data['duration']), reservation.id):
        return {"msg": "Зал занят"}, 400

    if data['status'] == ReservationStatusEnum.finished.name:
        if certificate:
            certificate.status = CertificateStatusEnum.redeemed

    queue: List['ReservationQueue'] = []
    if ReservationStatusEnum[data['status']] == ReservationStatusEnum.canceled:
        queue = search_available_items_from_queue(reservation)

        log_item = ReservationQueueViewLog(reservation=reservation, user=user)
        for queue_item in queue:
            queue_item.view_logs.append(log_item)
            db.session.add(queue_item)

    fields_to_set = ['duration', 'count', 'film', 'note']

    old_values = dump_reservation_to_update_log(reservation, reservation.guest)
    reservation.date = new_date
    reservation.room = room
    reservation.guest = guest
    reservation.certificate = certificate
    reservation.status = ReservationStatusEnum[data["status"]]
    reservation.sum_rent = data["rent"]

    for field in fields_to_set:
        setattr(reservation, field, data[field])

    new_values = dump_reservation_to_update_log(reservation, guest)
    update_log = UpdateLogs(reservation_id=reservation.id,
                            author=update_author, new=new_values, old=old_values)

    try:
        db.session.add(reservation)
        db.session.add(update_log)
        db.session.commit()
        return jsonify([queue_item.id for queue_item in queue]), 200
    except:
        return {"message": "Непредвиденная ошибка"}, 400
