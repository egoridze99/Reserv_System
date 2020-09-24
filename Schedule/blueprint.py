import builtins
import json

from flask import Blueprint, jsonify, request

from Schedule.utils import count_money, get_sum_of_checkouts, get_money_record, is_date_in_last, check_the_taking
from app import db
from models import *

schedule = Blueprint('schedule', __name__)


@schedule.route('/rooms')
def get_rooms():
    rooms = Room.query.all()
    room_names = [room.name for room in rooms]

    return jsonify(room_names)


@schedule.route('/seans')
def get_seans():
    room = request.args.get('room')
    date = request.args.get('date')

    if not room or not date:
        return {"message": "Не все данные"}, 400

    if room == 'all':
        seanses = Reservation.query.filter(Reservation.date == date).all()
    else:
        seanses = Reservation.query.join(Room).filter(Room.name == room).filter(Reservation.date == date).all()

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


@schedule.route('/seans/<id>', methods=['PUT'])
def update_seans(id):
    data = request.data
    data = json.loads(data)

    seans = Reservation.query.filter(Reservation.id == id).all()
    room = Room.query.filter(Room.name == data['room']).first()
    guest = Guest.query.filter(Guest.telephone == data['guest']['tel']).first()
    time = datetime.strptime(data['time'], '%H:%M').time()

    if guest is None:
        guest = Guest(name=data['guest']['name'], telephone=data['guest']['tel'])
        db.session.add(guest)

    if len(seans) == 0:
        return {"message": "Error"}, 400

    seans = seans[0]
    checkouts = []
    date = seans.date

    if seans.status == ReservStatusEnum.finished:
        return {"message": "Нельзя изменять завершенные сеансы!"}, 400

    if data['card'] == 0 \
            and data['cash'] == 0 \
            and data['status'] == ReservStatusEnum.finished.name \
            and data['rent'] != 0:
        return {"message": "Клиент не заплатил!"}, 400

    if date < datetime.now().date() and data['status'] != ReservStatusEnum.finished.name:
        return {"message": "Вы пытаетесь отредактировать старый сеанс!"}, 400

    if date > datetime.now().date() and data['status'] == ReservStatusEnum.finished.name:
        return {"message": "Как может завершиться сеанс в будещем?)"}, 400

    for check in data['checkouts']:
        if 'new' not in check:
            new_check = Checkout.query.filter(Checkout.id == check['id']).first()
            new_check.summ = check['summ']
            new_check.description = check['note']
            checkouts.append(new_check)
        else:
            new_check = Checkout(summ=check['summ'], description=check['note'])
            checkouts.append(new_check)

    if data['status'] == ReservStatusEnum.finished.name:
        sum_of_checkouts = get_sum_of_checkouts(checkouts)

        money = count_money(date, data['rent'], data['cash'], data['card'], sum_of_checkouts)
        if money is None:
            return {"message": "Произошла ошибка. Попробуйте снова"}, 400

    seans.time = datetime.strptime(data['time'], '%H:%M').time()
    seans.duration = data['duration']
    seans.count = data['count']
    seans.film = data['film']
    seans.note = data['note']
    seans.status = ReservStatusEnum[data['status']]
    seans.sum_rent = data['rent']
    seans.card = data['card']
    seans.cash = data['cash']
    seans.room = room
    seans.guest = guest
    seans.checkout = checkouts

    try:
        db.session.add(seans)
        db.session.commit()
    except builtins.TypeError:
        return {"message": "Непредвиденная ошибка"}, 400

    return {"message": "ok"}, 200


@schedule.route('/seans', methods=['POST'])
def create_seans():
    data = request.data
    data = json.loads(data)

    room = Room.query.filter(Room.name == data['room']).first()
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

    reserv = Reservation(
        time=time,
        date=date,
        duration=data['duration'],
        count=data['count'],
        film=data['film'],
        note=data['note'],
        sum_rent=data['rent'],
        room=room,
        guest=guest
    )
    db.session.add(reserv)
    try:
        db.session.commit()
        return {"message": "ok"}, 200
    except Exception:
        return {"message": "error"}, 400


@schedule.route('/money')
def get_money():
    date = request.args.get("date")
    money = get_money_record(date)

    return money, 200