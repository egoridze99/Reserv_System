from datetime import datetime, timedelta, time
from typing import Optional

from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from domains.reservation.handlers.utils import check_not_payment, check_the_taking, get_sum_of_checkouts, \
    dump_reservation_to_update_log
from db import db
from models import EmployeeRoleEnum, Reservation, Room, Guest, Certificate, CertificateStatusEnum, \
    ReservationStatusEnum, Checkout, UpdateLogs
from utils.count_money import count_money
from utils.parse_json import parse_json
from typings import UserJwtIdentity


def update_reservation(reservation_id: str):
    data = parse_json(request.data)
    identity: 'UserJwtIdentity' = get_jwt_identity()

    role = identity["role"]
    update_author = identity["name"]

    cinema_id = data["cinema_id"]

    if EmployeeRoleEnum[role] == EmployeeRoleEnum.operator:
        return {"message": "У вас не хватает прав на это"}, 403

    reservation = Reservation.query.filter(Reservation.id == reservation_id).first()
    room = Room.query.filter(Room.id == data['room']['id']).first()
    guest = Guest.query.filter(Guest.telephone == data['guest']['tel']).first()

    if guest is None:
        guest = Guest(name=data['guest']['name'], telephone=data['guest']['tel'])
        db.session.add(guest)

    checkouts = []
    date = reservation.date
    new_date = datetime.strptime(f"{data['date']} {data['time']}", '%Y-%m-%d %H:%M')

    certificate = None
    certificate_ident = data["certificate_ident"]
    if certificate_ident:
        certificate: Optional['Certificate'] = Certificate.query.filter(Certificate.ident == certificate_ident).first()

        if not certificate:
            return jsonify({"msg": "Сертификат не найден"}), 404

    if certificate and certificate != reservation.certificate:
        if certificate.status != CertificateStatusEnum.active:
            return {"msg": "Вы пытаетесь добавить погашенный сертификат"}, 400

    if reservation.status == ReservationStatusEnum.finished \
            and role != EmployeeRoleEnum.root.name:
        return {"msg": "Нельзя изменять завершенные сеансы!"}, 400

    if check_not_payment(role, data, certificate):
        return {"msg": "Клиент не заплатил!"}, 400

    if date < (datetime.now() - timedelta(days=1)).date() \
            and data['status'] != ReservationStatusEnum.finished.name \
            and role != EmployeeRoleEnum.root.name:
        return {"msg": "Вы пытаетесь отредактировать старый сеанс!"}, 400

    if date > datetime.now().date() and data['status'] == ReservationStatusEnum.finished.name \
            and role != EmployeeRoleEnum.root.name:
        return {"msg": "Как может завершиться сеанс в будещем?)"}, 400

    if check_the_taking(new_date, room, new_date.time(), float(data['duration']), id):
        return {"msg": "Зал занят"}, 400

    for check in data['checkouts']:
        if 'id' in check:
            new_check = Checkout.query.filter(Checkout.id == check['id']).first()
            new_check.sum = check['sum']
            new_check.description = check['note']
            checkouts.append(new_check)
        else:
            new_check = Checkout(sum=check['sum'], description=check['note'])
            checkouts.append(new_check)

    if data['status'] == ReservationStatusEnum.finished.name:
        sum_of_checkouts = get_sum_of_checkouts(checkouts)
        reservation_end_date = datetime.combine(reservation.date, reservation.time) + \
                               timedelta(hours=reservation.duration)

        cashier_date = reservation.date
        if reservation_end_date.time() <= time(8) and reservation.date == reservation_end_date.date():
            cashier_date = reservation_end_date.date() - timedelta(days=1)

        money = count_money(cashier_date, cinema_id, data['rent'], data['cash'], data['card'], sum_of_checkouts)
        if money is None:
            return {"message": "Произошла ошибка. Попробуйте снова"}, 400
        if certificate:
            certificate.status = CertificateStatusEnum.redeemed

        db.session.add(money)

    if data['status'] == ReservationStatusEnum.canceled.name:
        print("Ща че то буит")

    old_values = dump_reservation_to_update_log(reservation)
    reservation.date = new_date.date()
    reservation.time = new_date.time()
    reservation.duration = data['duration']
    reservation.count = data['count']
    reservation.film = data['film']
    reservation.note = data['note']
    reservation.status = ReservationStatusEnum[data['status']]
    reservation.sum_rent = data['rent']
    reservation.card = data['card']
    reservation.cash = data['cash']
    reservation.room = room
    reservation.guest = guest
    reservation.checkout = checkouts
    reservation.certificate = certificate
    new_values = dump_reservation_to_update_log(reservation)
    update_log = UpdateLogs(reservation_id=reservation.id, created_at=datetime.today().strftime("%d-%m-%Y %H:%M:%S"),
                            author=update_author, new=new_values, old=old_values)

    try:
        db.session.add(reservation)
        db.session.add(update_log)
        db.session.commit()
        return Reservation.to_json(reservation), 200
    except:
        return {"message": "Непредвиденная ошибка"}, 400
