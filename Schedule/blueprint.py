import builtins
import json

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from Schedule.utils import count_money, get_sum_of_checkouts, get_money_record, is_date_in_last, check_the_taking, \
    check_not_payment
from app import db
from models import *
from utils.parse_json import parse_json

schedule_blueprint = Blueprint('schedule_blueprint', __name__)


@schedule_blueprint.route('/cinemas')
@jwt_required
def get_cinemas():
    cinemas = Cinema.query.all()
    return jsonify([Cinema.toJson(cinema) for cinema in cinemas])


@schedule_blueprint.route('/reservation')
@jwt_required
def get_reservations():
    room: 'Room' = json.loads(request.args.get('room'))
    date = request.args.get('date')
    cinema_id = request.args.get('cinema_id')

    if not room or not date:
        return {"message": "Не все данные"}, 400

    if room["id"] == -1:
        seanses = Reservation.query.join(Room).filter(Reservation.date == date).filter(Room.cinema_id == cinema_id).all()
    else:
        seanses = Reservation.query.join(Room).filter(Room.id == room["id"]).filter(Reservation.date == date).all()

    return jsonify([Reservation.toJson(seans) for seans in seanses]), 200


@schedule_blueprint.route('/reservation/search')
@jwt_required
def search_reservations():
    statuses: list[ReservationStatusEnum] = request.args.get('status')
    rooms: list[Room] = request.args.get('room')
    ids: list[str] = request.args.get('ids')
    telephones: list[str] = request.args.get('telephones')
    start_date: str = request.args.get('date_from')
    end_date: str = request.args.get('date_to')

    reservation_query = Reservation.query.join(Room).join(Guest)

    if statuses:
        statuses = [ReservationStatusEnum[status] for status in json.loads(statuses)]
        reservation_query = reservation_query.filter(Reservation.status.in_(statuses))

    if rooms:
        rooms_id = [room["id"] for room in json.loads(rooms)]
        reservation_query = reservation_query.filter(Reservation.room_id.in_(rooms_id))

    if ids:
        ids = json.loads(ids)
        reservation_query = reservation_query.filter(Reservation.id.in_(ids))

    if telephones:
        telephones = json.loads(telephones)
        reservation_query = reservation_query.filter(Guest.telephone.in_(telephones))

    if start_date:
        reservation_query = reservation_query.filter(Reservation.date >= start_date)

    if end_date:
        reservation_query = reservation_query.filter(Reservation.date <= end_date)

    reservations = reservation_query.all()

    return jsonify([Reservation.toJson(reservation) for reservation in reservations]), 200


@schedule_blueprint.route('/reservation/<id>', methods=['PUT'])
@jwt_required
def update_reservation(id):
    data = parse_json(request.data)
    role = get_jwt_identity()["role"]
    cinema_id = data["cinema_id"]
    update_author = get_jwt_identity()["name"]

    if EmployeeRoleEnum[role] == EmployeeRoleEnum.operator:
        return {"message": "У вас не хватает прав на это"}, 403

    seans = Reservation.query.filter(Reservation.id == id).first()
    room = Room.query.filter(Room.id == data['room']['id']).first()
    guest = Guest.query.filter(Guest.telephone == data['guest']['tel']).first()

    if guest is None:
        guest = Guest(name=data['guest']['name'], telephone=data['guest']['tel'])
        db.session.add(guest)

    old_checkouts = seans.checkout
    checkouts = []
    date = seans.date

    new_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    new_time = datetime.strptime(data['time'], '%H:%M').time()

    certificate = None
    certificate_ident = data["certificate_ident"]
    if certificate_ident:
        certificate: 'Certificate' = Certificate.query.filter(Certificate.ident == certificate_ident).first()

        if not certificate:
            return jsonify({"msg": "Сертификат не найден"}), 404

    if certificate and certificate != seans.certificate:
        if certificate.status != CertificateStatusEnum.active:
            return {"msg": "Вы пытаетесь добавить погашенный сертификат"}, 400

    if seans.status == ReservationStatusEnum.finished \
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

    if check_the_taking(new_date, room, new_time, float(data['duration']), id):
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

        money = count_money(date, cinema_id, data['rent'], data['cash'], data['card'], sum_of_checkouts)
        if money is None:
            return {"message": "Произошла ошибка. Попробуйте снова"}, 400
        if certificate:
            certificate.status = CertificateStatusEnum.redeemed

    oldValues = json.dumps({
        "time": str(seans.time)[:-3],
        "room": seans.room.name,
        "duration": seans.duration,
        "count": seans.count,
        "film": seans.film,
        "note": seans.note,
        "status": seans.status.name,
        "sum_rent": seans.sum_rent,
        "card": seans.card,
        "cash": seans.cash,
        "guest_name": seans.guest.name,
        "guest_telephone": seans.guest.telephone,
        "certificate_ident": seans.certificate.ident if seans.certificate else None,
        "checkouts": [{"description": item.description, "sum": item.sum} for item in old_checkouts]
    })

    seans.date = new_date
    seans.time = new_time
    seans.duration = data['duration']
    seans.count = data['count']
    seans.film = data['film']
    seans.note = data['note']
    seans.status = ReservationStatusEnum[data['status']]
    seans.sum_rent = data['rent']
    seans.card = data['card']
    seans.cash = data['cash']
    seans.room = room
    seans.guest = guest
    seans.checkout = checkouts
    seans.certificate = certificate

    newValues = json.dumps({
        "time": str(seans.time)[:-3],
        "room": seans.room.name,
        "duration": seans.duration,
        "count": seans.count,
        "film": seans.film,
        "note": seans.note,
        "status": seans.status.name,
        "sum_rent": seans.sum_rent,
        "card": seans.card,
        "cash": seans.cash,
        "guest_name": seans.guest.name,
        "guest_telephone": seans.guest.telephone,
        "checkouts": [{"description": item.description, "sum": item.sum} for item in checkouts],
        "certificate_ident": seans.certificate.ident if seans.certificate else None,
    })

    updateLog = UpdateLogs(reservation_id=seans.id, created_at=datetime.today().strftime("%d-%m-%Y %H:%M:%S"), author=update_author, new=newValues, old=oldValues)

    try:
        db.session.add(seans)
        db.session.add(updateLog)
        db.session.commit()
    except builtins.TypeError:
        return {"message": "Непредвиденная ошибка"}, 400

    return Reservation.toJson(seans), 200


@schedule_blueprint.route('/reservation', methods=['POST'])
@jwt_required
def create_reservation():
    data = parse_json(request.data)
    name = get_jwt_identity()["name"]
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

    reserv = Reservation(
        time=time,
        date=date,
        duration=data['duration'],
        count=data['count'],
        film=data['film'],
        note=data['note'],
        sum_rent=data['rent'],
        room=room,
        guest=guest,
        author=name,
        certificate=certificate,
        created_at=datetime.today().strftime("%d-%m-%Y")
    )
    db.session.add(reserv)
    try:
        db.session.commit()
        return Reservation.toJson(reserv), 200
    except Exception:
        return {"msg": "error"}, 400


@schedule_blueprint.route('/money')
@jwt_required
def get_money():
    date = request.args.get("date")
    cinema_id = request.args.get("cinema_id")

    money = get_money_record(date, cinema_id)

    return money, 200