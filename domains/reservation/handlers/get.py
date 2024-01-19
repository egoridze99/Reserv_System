from datetime import datetime, timedelta

from flask import request, jsonify, json

from models import Reservation, Room, ReservationStatusEnum, Guest, UpdateLogs
from utils.filter_items_from_another_shift import filter_items_from_another_shift


def get_reservations():
    room_id = request.args.get('room_id')
    date = datetime.strptime(request.args.get('date'), '%Y-%m-%d').date()
    cinema_id = request.args.get('cinema_id')

    if not date or not cinema_id:
        return {"message": "Не все данные"}, 400

    reservations = Reservation.query.join(Room).filter(Reservation.date.in_([date, date + timedelta(days=1)]))

    if not room_id:
        reservations = reservations.filter(Room.cinema_id == cinema_id).all()
    else:
        reservations = reservations.filter(Room.id == room_id).all()

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
        reservation_query = reservation_query.filter(Reservation.room_id.in_(json.loads(rooms)))

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


def get_logs(reservation_id):
    logs = UpdateLogs.query.filter(UpdateLogs.reservation_id == reservation_id).all()
    logs = [UpdateLogs.to_json(log) for log in logs]
    logs.sort(key=lambda x: datetime.strptime(x['created_at'], '%d-%m-%Y %H:%M'))

    return jsonify(logs)