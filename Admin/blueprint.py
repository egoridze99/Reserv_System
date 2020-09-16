import hashlib

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required

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

    user = AdminUser.query.filter(AdminUser.login == login).first()

    if not user:
        return jsonify({"msg": "Неверный логин"}), 400

    password = hashlib.md5(password.encode()).hexdigest()

    if password != user.password:
        return jsonify({"msg": "Неверный пароль"}), 400

    jwt = create_access_token(identity=login)

    return jsonify({"token": "Bearer " + jwt}), 200


@admin.route("/common")
@jwt_required
def get_common_info():
    untill = request.args.get('untill')
    till = request.args.get('till')

    if untill == till:
        reservs = Reservation.query\
            .filter(Reservation.date == till)\
            .filter(Reservation.status != ReservStatusEnum.canceled)\
            .all()
    else:
        reservs = Reservation.query\
            .filter(Reservation.date >= untill)\
            .filter(Reservation.date <= till) \
            .filter(Reservation.status != ReservStatusEnum.canceled)\
            .all()

    duration = {'total': 0}
    money = {'total': 0}
    checkout = {'total': 0}

    for reserv in reservs:
        room = reserv.room.name

        if room not in duration:
            duration[room] = float(reserv.duration)
        else:
            duration[room] += float(reserv.duration)
        duration['total'] += float(reserv.duration)

        if room not in money:
            money[room] = {
                "cash": float(reserv.cash),
                "card": float(reserv.card),
                "rent": int(reserv.sum_rent)
            }
        else:
            money[room]["cash"] += float(reserv.cash)
            money[room]["card"] += float(reserv.card)
            money[room]["rent"] += int(reserv.sum_rent)
        money['total'] += int(reserv.sum_rent)

        if room not in checkout:
            checkout[room] = 0
            for item in reserv.checkout:
                checkout[room] += float(item.summ)
        else:
            for item in reserv.checkout:
                checkout[room] += float(item.summ)
        for item in reserv.checkout:
            checkout['total'] += float(item.summ)

    res = {
        "duration": duration,
        "money": money,
        "checkout": checkout
    }

    return jsonify(res), 200

@admin.route("/canceled")
@jwt_required
def get_canceled():
    untill = request.args.get('untill')
    till = request.args.get('till')

    if untill == till:
        seanses = Reservation.query\
            .filter(Reservation.date == till)\
            .filter(Reservation.status == ReservStatusEnum.canceled)\
            .all()
    else:
        seanses = Reservation.query\
            .filter(Reservation.date >= untill)\
            .filter(Reservation.date <= till) \
            .filter(Reservation.status == ReservStatusEnum.canceled)\
            .all()

    seanses = [{
        'id': seans.id,
        'date': seans.date,
        'time': str(seans.time)[:-3],
        'duration': seans.duration,
        'count': seans.count,
        'film': seans.film,
        'note': seans.note,
        'status': seans.status.name,
        'card': seans.card,
        'cash': seans.cash,
        'rent': seans.sum_rent,
        'guest': {
            "name": seans.guest.name,
            "tel": seans.guest.telephone
        },
        'checkout': [{
            'id': checkout.id,
            'summ': checkout.summ,
            'note': checkout.description,
        } for checkout in seans.checkout]
    } for seans in seanses]

    return jsonify(seanses), 200