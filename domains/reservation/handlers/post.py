from datetime import datetime

from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from db import db
from domains.reservation.handlers.utils import check_the_taking
from models import EmployeeRoleEnum, Room, Guest, Certificate, CertificateStatusEnum, Reservation, User
from typings import UserJwtIdentity
from utils.is_date_in_last import is_date_in_last
from utils.parse_json import parse_json


def create_reservation():
    identity: UserJwtIdentity = get_jwt_identity()
    data = parse_json(request.data)
    role = get_jwt_identity()["role"]

    if EmployeeRoleEnum[role] == EmployeeRoleEnum.operator:
        return {"message": "У вас не хватает прав на это"}, 403

    room = Room.query.filter(Room.id == data['room']['id']).first()
    guest = Guest.query.filter(Guest.telephone == data['guest']['tel']).first()

    if guest is None:
        guest = Guest(name=data['guest']['name'], telephone=data['guest']['tel'])
        db.session.add(guest)

    date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    time = datetime.strptime(data['time'], '%H:%M').time()

    if check_the_taking(date, room, time, float(data['duration'])):
        return {"msg": "Зал занят"}, 400

    if is_date_in_last(date):
        return {"msg": "Дата уже прошла"}, 400

    certificate = None
    certificate_ident = data["certificate_ident"]
    if certificate_ident:
        certificate = Certificate.query.filter(Certificate.ident == certificate_ident).first()

        if not certificate:
            return jsonify({"msg": "Сертификат не найден"}), 404

    if certificate and certificate.status != CertificateStatusEnum.active:
        return {"msg": "Сертификат уже погашен"}, 400

    author = User.query.filter(User.id == int(identity["id"])).first()

    reservation = Reservation(
        time=time,
        date=date,
        duration=data['duration'],
        count=data['count'],
        film=data['film'],
        note=data['note'],
        sum_rent=data['rent'],
        room=room,
        guest=guest,
        author=author,
        certificate=certificate,
        created_at=datetime.today().strftime("%d-%m-%Y")
    )
    db.session.add(reservation)
    try:
        db.session.commit()
        return Reservation.to_json(reservation), 200
    except Exception:
        return {"msg": "error"}, 400
