import re

from flask import request, jsonify
from sqlalchemy import func

from db import db
from domains.admin.handlers.queries import *
from models import Guest, Cinema, Reservation, Room


PAYMENT_KEYS = ('cash', 'card', 'sbp', 'total')


def _cinema_room(source, cinema_id, room_id):
    return source.get(cinema_id, {}).get('rooms', {}).get(room_id)


def _split_total(by_reservations, by_cinema, cinema_id):
    reservations = by_reservations.get(cinema_id, {}).get('total') or 0
    cinema = by_cinema.get(cinema_id, {}).get('total') or 0

    return {"reservations": reservations, "cinema": cinema, 'total': reservations + cinema}


def get_common_info():
    until = request.args.get('until')
    till = request.args.get('till')

    cinemas = Cinema.query.all()

    durations = get_duration_query(until, till)

    reservations_income = get_reservation_money_query(until, till, True)
    reservations_expense = get_reservation_money_query(until, till, False)

    cinema_income = get_cinema_money_query(until, till, True)
    cinema_expense = get_cinema_money_query(until, till, False)

    reservation_refunds = get_reservation_money_query(until, till, True, True)
    cinema_refunds = get_cinema_money_query(until, till, True, True)

    result = []

    for cinema in cinemas:
        is_cinema_filled = False
        cinema_data = {'cinema_id': cinema.id, 'cinema_name': cinema.name}

        if cinema.id in durations:
            is_cinema_filled = True
            cinema_data['total_duration'] = durations[cinema.id]['sum']

        if cinema.id in reservations_income or cinema.id in cinema_income:
            is_cinema_filled = True
            income = {}

            for name, source in (("reservations", reservations_income), ("cinema", cinema_income)):
                if cinema.id in source:
                    income[name] = {key: source[cinema.id][key] for key in PAYMENT_KEYS}

            income['total'] = {key: sum(part[key] or 0 for part in income.values()) for key in PAYMENT_KEYS}
            cinema_data["income"] = income

        if cinema.id in reservations_expense or cinema.id in cinema_expense:
            is_cinema_filled = True
            cinema_data["expense"] = _split_total(reservations_expense, cinema_expense, cinema.id)

        if cinema.id in reservation_refunds or cinema.id in cinema_refunds:
            is_cinema_filled = True
            cinema_data["refunds"] = _split_total(reservation_refunds, cinema_refunds, cinema.id)

        for room in cinema.rooms:
            room_data = {'room_id': room.id, 'room_name': room.name}

            duration = _cinema_room(durations, cinema.id, room.id)
            income = _cinema_room(reservations_income, cinema.id, room.id)
            expense = _cinema_room(reservations_expense, cinema.id, room.id)
            refunds = _cinema_room(reservation_refunds, cinema.id, room.id)

            if duration is not None:
                room_data['total_duration'] = duration

            if income:
                room_data["income"] = income

            if expense:
                room_data["expense"] = expense['total']

            if refunds:
                is_cinema_filled = True
                room_data["refunds"] = refunds['total']

            if duration is not None or income or expense:
                cinema_data.setdefault('rooms', []).append(room_data)

        if is_cinema_filled:
            result.append(cinema_data)

    return jsonify(result), 200


def get_telephones():
    phone_pattern = r'[\+]?[78][\-]?[\d]{3}[\-]?[\d]{3}[\-]?[\d]{2}[\-]?[\d]{2}'

    city = request.args.get('city')
    min_visits = request.args.get('min_visits')
    last_visit_threshold = request.args.get('last_visit_threshold')
    ignore_before_date = request.args.get('ignore_before_date')

    last_visit_subquery = (
        db.session.query(
            Reservation.guest_id,
            func.max(Reservation.date).label('last_visit_date')
        )
        .group_by(Reservation.guest_id)
        .subquery()
    )

    query = (
        db.session.query(Guest)
        .join(Reservation, Guest.id == Reservation.guest_id)
        .join(Room, Reservation.room_id == Room.id)
        .join(Cinema, Cinema.id == Room.cinema_id)
        .join(last_visit_subquery, Guest.id == last_visit_subquery.c.guest_id)
    )

    if city is not None:
        city = int(city)
        query = query.filter(Cinema.city_id == city)

    if last_visit_threshold is not None:
        query = query.filter(last_visit_subquery.c.last_visit_date <= last_visit_threshold)

    if ignore_before_date is not None:
        query = query.filter(last_visit_subquery.c.last_visit_date >= ignore_before_date)

    query = query.group_by(Guest.id)

    if min_visits is not None:
        min_visits = int(min_visits)
        query = query.having(func.count(Reservation.id) >= min_visits)

    result = query.all()
    result = [guest.telephone for guest in result if re.fullmatch(phone_pattern, guest.telephone)]

    return jsonify({'data': result}), 200
