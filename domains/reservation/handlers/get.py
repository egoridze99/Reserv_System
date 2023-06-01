from datetime import datetime, timedelta

from flask import request, jsonify, json

from models import Reservation, Room, ReservationStatusEnum, Guest
from utils.filter_items_from_another_shift import filter_items_from_another_shift


def get_reservations():
    room = json.loads(request.args.get('room'))
    date = datetime.strptime(request.args.get('date'), '%Y-%m-%d').date()
    cinema_id = request.args.get('cinema_id')

    if not room or not date:
        return {"message": "Не все данные"}, 400

    reservations = Reservation.query.join(Room).filter(Reservation.date.in_([date, date + timedelta(days=1)]))

    if room["id"] == -1:
        reservations = reservations.filter(Room.cinema_id == cinema_id).all()
    else:
        reservations = reservations.filter(Room.id == room["id"]).all()

    reservations = filter(lambda x: filter_items_from_another_shift(x, date), reservations)

    return jsonify([Reservation.to_json(reservation) for reservation in reservations]), 200


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

    return jsonify([Reservation.to_json(reservation) for reservation in reservations]), 200
