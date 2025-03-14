from datetime import datetime, time, timedelta

from flask import request, jsonify, json
from sqlalchemy import text, func, cast, String

from models import Reservation, Room, ReservationStatusEnum, Guest, UpdateLogs, Cinema, City
from utils.convert_tz import convert_tz


def get_reservations():
    room_id = request.args.get('room_id')
    cinema_id = request.args.get('cinema_id')
    date = datetime.strptime(request.args.get('date'), '%Y-%m-%d').date()

    if not date or not cinema_id:
        return {"message": "Не все данные"}, 400

    cinema = Cinema.query.filter(Cinema.id == cinema_id).first()
    min_date = convert_tz(datetime.combine(date, time(8)), cinema.city.timezone, True)
    max_date = convert_tz(datetime.combine(date + timedelta(days=1), time(8)), cinema.city.timezone, True)

    reservations = Reservation.query.join(Room).join(Cinema).filter(
        func.datetime(Reservation.date, '+' + cast(Reservation.duration, String) + ' hours').between(min_date,
                                                                                                     max_date))

    if not room_id:
        reservations = reservations.filter(Cinema.id == cinema_id).all()
    else:
        reservations = reservations.filter(Room.id == room_id).all()

    return jsonify([Reservation.to_json(reservation) for reservation in reservations]), 200


def get_reservation_by_id(reservation_id: int):
    reservation = Reservation.query.filter(Reservation.id == reservation_id).first()

    return jsonify(Reservation.to_json(reservation)), 200


def search_reservations():
    statuses: list[ReservationStatusEnum] = request.args.get('status')
    rooms: list[Room] = request.args.get('room')
    ids: list[str] = request.args.get('ids')
    telephones: list[str] = request.args.get('telephones')
    start_date: str = request.args.get('date_from')
    end_date: str = request.args.get('date_to')
    created_start_date: str = request.args.get('created_start_date')
    created_end_date: str = request.args.get('created_end_date')

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
        start_date_as_date = datetime.combine(datetime.strptime(start_date, '%Y-%m-%d').date(), time(8))

        reservation_query = reservation_query.filter(
            func.datetime(func.datetime(Reservation.date, '+' + cast(Reservation.duration, String) + ' hours'),
                          City.timezone) > start_date_as_date)

    if end_date:
        end_date_as_date = datetime.combine(datetime.strptime(end_date, '%Y-%m-%d').date(), time(8)) + timedelta(days=1)

        reservation_query = reservation_query.filter(
            func.datetime(func.datetime(Reservation.date, '+' + cast(Reservation.duration, String) + ' hours'),
                          City.timezone) < end_date_as_date)

    if created_start_date:
        created_start_date_as_date = datetime.combine(datetime.strptime(created_start_date, '%Y-%m-%d').date(), time(8))

        reservation_query = reservation_query.filter(
            func.datetime(func.datetime(Reservation.created_at), City.timezone) > created_start_date_as_date)

    if created_end_date:
        created_end_date_as_date = datetime.combine(datetime.strptime(created_end_date, '%Y-%m-%d').date(),
                                                    time(8)) + timedelta(days=1)

        reservation_query = reservation_query.filter(
            func.datetime(func.datetime(Reservation.created_at),
                          City.timezone) < created_end_date_as_date)

    reservations = reservation_query.all()

    return jsonify([Reservation.to_json(reservation) for reservation in reservations]), 200


def get_logs(reservation_id):
    logs = UpdateLogs.query.filter(UpdateLogs.reservation_id == reservation_id).all()

    logs = [UpdateLogs.to_json(log) for log in logs]
    logs.sort(key=lambda x: x['created_at'])

    return jsonify(logs)
