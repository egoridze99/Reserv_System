import hashlib

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

    user = AdminUser.query.filter(AdminUser.login == login).first()

    if not user:
        return jsonify({"msg": "Неверный логин"}), 400

    password = hashlib.md5(password.encode()).hexdigest()

    if password != user.password:
        return jsonify({"msg": "Неверный пароль"}), 400

    jwt = create_access_token(identity={"login": login, "role": user.role}, expires_delta=timedelta(hours=6))

    return jsonify({"token": "Bearer " + jwt, "role": user.role}), 200


@admin.route("/common")
@jwt_required
def get_common_info():
    identity = get_jwt_identity()

    if identity["role"] != 1:
        return 403

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
    identity = get_jwt_identity()

    if identity["role"] != 1:
        return 403

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


@admin.route("/new_user", methods=["POST"])
@jwt_required
def new_user():
    identity = get_jwt_identity()

    if identity["role"] != 1:
        return 403

    login = request.json.get("login")
    password = request.json.get("password")

    user = AdminUser.query.filter(AdminUser.login == login).first()

    if not login:
        return {"msg": "Логин пустой"}, 400

    if not password:
        return {"msg": "Пароль пустой"}, 400

    if user:
        return {"msg": "Такой пользователь уже есть"}, 400

    password = hashlib.md5(password.encode()).hexdigest()
    user = AdminUser(login=login, password=password)

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
    seanses = [{
        'id': seans.id,
        'date': seans.date,
        'room': seans.room.name,
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