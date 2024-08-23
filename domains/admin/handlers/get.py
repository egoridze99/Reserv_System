import re

from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import func

from db import db
from domains.admin.handlers.queries import *
from models import EmployeeRoleEnum, Guest, Cinema, Reservation, Room


def get_common_info():
    identity = get_jwt_identity()
    role = identity["role"]

    if EmployeeRoleEnum[role] != EmployeeRoleEnum.root:
        return {"message": "Недостаточно прав"}, 403

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
            cinema_data["income"] = dict()

            all_by_card = 0
            all_by_cash = 0
            all_by_sbp = 0
            total = 0

            if cinema.id in reservations_income:
                all_by_card += reservations_income[cinema.id]['card'] or 0
                all_by_cash += reservations_income[cinema.id]['cash'] or 0
                all_by_sbp += reservations_income[cinema.id]['sbp'] or 0
                total += reservations_income[cinema.id]['total'] or 0

                cinema_data["income"]["reservations"] = {
                    'cash': reservations_income[cinema.id]['cash'],
                    'card': reservations_income[cinema.id]['card'],
                    'sbp': reservations_income[cinema.id]['sbp'],
                    'total': reservations_income[cinema.id]['total']
                }

            if cinema.id in cinema_income:
                all_by_card += cinema_income[cinema.id]['card'] or 0
                all_by_cash += cinema_income[cinema.id]['cash'] or 0
                all_by_sbp += cinema_income[cinema.id]['sbp'] or 0
                total += cinema_income[cinema.id]['total'] or 0

                cinema_data["income"]["cinema"] = {
                    'cash': cinema_income[cinema.id]['cash'],
                    'card': cinema_income[cinema.id]['card'],
                    'sbp': cinema_income[cinema.id]['sbp'],
                    'total': cinema_income[cinema.id]['total']
                }

            cinema_data["income"]['total'] = {
                'cash': all_by_cash,
                'card': all_by_card,
                'sbp': all_by_sbp,
                'total': total
            }

        if cinema.id in reservations_expense or cinema.id in cinema_expense:
            is_cinema_filled = True

            cinema_reservations_expense = 0
            if cinema.id in reservations_expense:
                cinema_reservations_expense = reservations_expense[cinema.id]['total'] or 0

            current_cinema_expense = 0
            if cinema.id in cinema_expense:
                current_cinema_expense = cinema_expense[cinema.id]['total'] or 0

            cinema_data["expense"] = {"reservations": cinema_reservations_expense,
                                      "cinema": current_cinema_expense,
                                      'total': cinema_reservations_expense + current_cinema_expense}

        if cinema.id in reservation_refunds or cinema.id in cinema_refunds:
            is_cinema_filled = True

            cinema_reservations_refunds = 0
            if cinema.id in reservation_refunds:
                cinema_reservations_refunds = reservation_refunds[cinema.id]['total'] or 0

            current_cinema_refunds = 0
            if cinema.id in cinema_refunds:
                current_cinema_refunds = cinema_refunds[cinema.id]['total'] or 0

            cinema_data["refunds"] = {"reservations": cinema_reservations_refunds, "cinema": current_cinema_refunds,
                                      'total': cinema_reservations_refunds + current_cinema_refunds}

        for room in cinema.rooms:
            is_room_filled = False

            room_data = {'room_id': room.id, 'room_name': room.name}

            if cinema.id in durations and room.id in durations[cinema.id]['rooms']:
                is_room_filled = True
                room_data['total_duration'] = durations[cinema.id]['rooms'][room.id]

            if cinema.id in reservations_income and room.id in reservations_income[cinema.id]['rooms']:
                is_room_filled = True

                room_data["income"] = {
                    'cash': reservations_income[cinema.id]['rooms'][room.id]['cash'],
                    'card': reservations_income[cinema.id]['rooms'][room.id]['card'],
                    'sbp': reservations_income[cinema.id]['rooms'][room.id]['sbp'],
                    'total': reservations_income[cinema.id]['rooms'][room.id]['total']
                }

            if cinema.id in reservations_expense and room.id in reservations_expense[cinema.id]['rooms']:
                is_room_filled = True
                room_data["expense"] = reservations_expense[cinema.id]['rooms'][room.id]['total']

            if cinema.id in reservation_refunds and room.id in reservation_refunds[cinema.id]['rooms']:
                is_cinema_filled = True
                room_data["refunds"] = reservation_refunds[cinema.id]['rooms'][room.id]['total']

            if is_room_filled:
                if 'rooms' not in cinema_data:
                    cinema_data['rooms'] = []

                cinema_data['rooms'].append(room_data)

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
