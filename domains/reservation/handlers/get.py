from datetime import datetime

from flask import request, jsonify, json
from sqlalchemy import text

from models import Reservation, Room, ReservationStatusEnum, Guest, UpdateLogs, Cinema, City


def get_reservations():
    room_id = request.args.get('room_id')
    date = datetime.strptime(request.args.get('date'), '%Y-%m-%d').date()
    cinema_id = request.args.get('cinema_id')

    if not date or not cinema_id:
        return {"message": "Не все данные"}, 400

    reservations = Reservation.query.join(Room).join(Cinema).join(City).filter(
        text(
            "date(get_shift_date(reservation.date, city.timezone, reservation.duration)) = :target")).params(
        target=date)

    if not room_id:
        reservations = reservations.filter(Cinema.id == cinema_id).all()
    else:
        reservations = reservations.filter(Room.id == room_id).all()

    return jsonify([Reservation.to_json(reservation) for reservation in reservations]), 200


def search_reservations():
    statuses: list[ReservationStatusEnum] = request.args.get('status')
    rooms: list[Room] = request.args.get('room')
    ids: list[str] = request.args.get('ids')
    telephones: list[str] = request.args.get('telephones')
    start_date: str = request.args.get('date_from')
    end_date: str = request.args.get('date_to')

    reservation_query = Reservation.query.join(Room).join(Guest).join(Cinema).join(City)

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
        start_date_as_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        reservation_query = reservation_query.filter(text(
            "date(get_shift_date(reservation.date, city.timezone, reservation.duration)) >= :start_date")).params(
            start_date=start_date_as_date)

    if end_date:
        end_date_as_date = datetime.strptime(end_date, '%Y-%m-%d')
        reservation_query = reservation_query.filter(text(
            "date(get_shift_date(reservation.date, city.timezone, reservation.duration)) <= :end_date")).params(
            end_date=end_date_as_date)

    reservations = reservation_query.all()

    return jsonify([Reservation.to_json(reservation) for reservation in reservations]), 200


def get_logs(reservation_id):
    reservation = Reservation.query.filter(Reservation.id == reservation_id).first()
    logs = UpdateLogs.query.filter(UpdateLogs.reservation_id == reservation.id).all()

    logs = [UpdateLogs.to_json(log, reservation.room.cinema.city.timezone) for log in logs]
    logs.sort(key=lambda x: x['created_at'])

    return jsonify(logs)
