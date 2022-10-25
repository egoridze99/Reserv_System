import hashlib
import re

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_claims, get_jwt_identity

from models import *

admin = Blueprint('myadmin', __name__)


@admin.route('/login', methods=["POST"])
def index():
    if not request.is_json:
        return jsonify({"msg": "Ошибка сервера"}), 400

    login = request.json.get('login', None)
    password = request.json.get('password', None)

    if not login:
        return jsonify({"msg": "Не введен логин"}), 400
    if not password:
        return jsonify({"msg": "Не введен пароль"}), 400

    user = User.query.filter(User.login == login).first()

    if not user:
        return jsonify({"msg": "Неверный логин"}), 400

    password = hashlib.md5(password.encode()).hexdigest()

    if password != user.password:
        return jsonify({"msg": "Неверный пароль"}), 400

    jwt = create_access_token(identity={
        "login": login,
        "role": user.role.value,
        "name": f"{user.name} {user.surname}"
    }, expires_delta=timedelta(hours=6))

    return {"jwt": jwt}, 200


@admin.route("/common")
@jwt_required
def get_common_info():
    identity = get_jwt_identity()
    role = identity["role"]

    if EmployeeRoleEnum[role] != EmployeeRoleEnum.root:
        return {"message": "Недостаточно прав"}, 403

    untill = request.args.get('untill')
    till = request.args.get('till')

    if untill == till:
        reservs = Reservation.query\
            .filter(Reservation.date == till)\
            .filter(Reservation.status != ReservationStatusEnum.canceled)\
            .all()
    else:
        reservs = Reservation.query\
            .filter(Reservation.date >= untill)\
            .filter(Reservation.date <= till) \
            .filter(Reservation.status != ReservationStatusEnum.canceled)\
            .all()

    duration = {'total': 0, "room": {}, "cinema": {}}
    money = {'total': 0, "room": {}, "cinema": {}}
    checkout = {'total': 0, "room": {}, "cinema": {}}

    for reserv in reservs:
        room = reserv.room.name
        cinema = reserv.room.cinema.name

        if cinema not in duration["cinema"]:
            duration["cinema"][cinema] = float(reserv.duration)
        else:
            duration["cinema"][cinema] += float(reserv.duration)

        if room not in duration["room"]:
            duration["room"][room] = float(reserv.duration)
        else:
            duration["room"][room] += float(reserv.duration)
        duration['total'] += float(reserv.duration)

        if cinema not in money["cinema"]:
            money["cinema"][cinema] = {
                "cash": float(reserv.cash),
                "card": float(reserv.card),
                "rent": int(reserv.sum_rent)
            }
        else:
            money["cinema"][cinema]["cash"] += float(reserv.cash)
            money["cinema"][cinema]["card"] += float(reserv.card)
            money["cinema"][cinema]["rent"] += int(reserv.sum_rent)

        if room not in money["room"]:
            money["room"][room] = {
                "cash": float(reserv.cash),
                "card": float(reserv.card),
                "rent": int(reserv.sum_rent)
            }
        else:
            money["room"][room]["cash"] += float(reserv.cash)
            money["room"][room]["card"] += float(reserv.card)
            money["room"][room]["rent"] += int(reserv.sum_rent)
        money['total'] += int(reserv.sum_rent)

        if cinema not in checkout["cinema"]:
            checkout["cinema"][cinema] = 0
            for item in reserv.checkout:
                checkout["cinema"][cinema] += float(item.sum)
        else:
            for item in reserv.checkout:
                checkout["cinema"][cinema] += float(item.sum)

        if room not in checkout["room"]:
            checkout["room"][room] = 0
            for item in reserv.checkout:
                checkout["room"][room] += float(item.sum)
        else:
            for item in reserv.checkout:
                checkout["room"][room] += float(item.sum)
        for item in reserv.checkout:
            checkout['total'] += float(item.sum)

    res = {
        "duration": duration,
        "money": money,
        "checkout": checkout
    }

    return jsonify(res), 200


@admin.route("/statused")
@jwt_required
def get_canceled():
    identity = get_jwt_identity()
    role = identity["role"]

    if EmployeeRoleEnum[role] != EmployeeRoleEnum.root:
        return {"message": "Недостаточно прав"}, 403

    untill = request.args.get('untill')
    till = request.args.get('till')
    mode = request.args.get('mode')

    if mode == 'canceled':
        if untill == till:
            seanses = Reservation.query\
                .filter(Reservation.date == till)\
                .filter(Reservation.status == ReservationStatusEnum.canceled)\
                .all()
        else:
            seanses = Reservation.query\
                .filter(Reservation.date >= untill)\
                .filter(Reservation.date <= till) \
                .filter(Reservation.status == ReservationStatusEnum.canceled)\
                .all()
    else:
        if untill == till:
            seanses = Reservation.query\
                .filter(Reservation.date == till)\
                .filter(Reservation.status != ReservationStatusEnum.canceled) \
                .filter(Reservation.status != ReservationStatusEnum.finished) \
                .all()
        else:
            seanses = Reservation.query\
                .filter(Reservation.date >= untill)\
                .filter(Reservation.date <= till) \
                .filter(Reservation.status != ReservationStatusEnum.canceled) \
                .filter(Reservation.status != ReservationStatusEnum.finished) \
                .all()

    seanses = [Reservation.toJson(seans) for seans in seanses]

    return jsonify(seanses), 200


@admin.route("/new_user", methods=["POST"])
@jwt_required
def new_user():
    identity = get_jwt_identity()
    role = identity["role"]

    if EmployeeRoleEnum[role] != EmployeeRoleEnum.root:
        return {"message": "Недостаточно прав"}, 403

    login = request.json.get("login")
    password = request.json.get("password")
    name = request.json.get("name")
    surname = request.json.get("surname")
    role = request.json.get("role")

    user = User.query.filter(User.login == login).first()

    if not login:
        return {"msg": "Логин пустой"}, 400

    if not password:
        return {"msg": "Пароль пустой"}, 400

    if not name:
        return {"msg": "Имя пустое"}, 400

    if not surname:
        return {"msg": "Фамилия пустая"}, 400

    if user:
        return {"msg": "Такой пользователь уже есть"}, 400

    password = hashlib.md5(password.encode()).hexdigest()
    user = User(login=login, password=password, name=name, surname=surname, role=EmployeeRoleEnum[role].value)

    db.session.add(user)
    try:
        db.session.commit()
        return {"message": "ok"}, 200
    except Exception:
        return {"message": "error"}, 400


@admin.route("/reservs", methods=["GET"])
@jwt_required
def reservs_with_number():
    telephone = request.args.get("telephone")
    seanses = Reservation.query.join(Guest).filter(Guest.telephone == telephone).all()
    seanses = [Reservation.toJson(seans) for seans in seanses]

    return jsonify(seanses), 200

@admin.route("/telephones")
@jwt_required
def get_telephones():
    phone_pattern = r'[\+]?[78][\-]?[\d]{3}[\-]?[\d]{3}[\-]?[\d]{2}[\-]?[\d]{2}'
    guests = Guest.query.all()
    result = [guest.telephone for guest in guests if re.fullmatch(phone_pattern, guest.telephone)]

    return jsonify(result), 200

@admin.route("/logs/<reservation_id>")
@jwt_required
def get_logs(reservation_id):
    logs = UpdateLogs.query.filter(UpdateLogs.reservation_id == reservation_id).all()
    logs = [log.toJson() for log in logs]
    logs.sort(key=lambda x: datetime.strptime(x['created_at'], '%d-%m-%Y %H:%M:%S'))
    return jsonify(logs)