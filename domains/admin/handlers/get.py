import re

from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import func, text

from db import db
from domains.admin.handlers.queries import *
from models import EmployeeRoleEnum, Guest, Room, Cinema, Reservation, ReservationStatusEnum, City
from utils.sa_query_result_to_dict import sa_query_result_to_dict


def get_common_info():
    identity = get_jwt_identity()
    role = identity["role"]

    if EmployeeRoleEnum[role] != EmployeeRoleEnum.root:
        return {"message": "Недостаточно прав"}, 403

    until = request.args.get('untill')
    till = request.args.get('till')
    area = request.args.get('area')
    print(get_money_query(area, until, till, True))
    return jsonify({
        "duration": get_duration_query(area, until, till),
        "money": sa_query_result_to_dict(db.session.execute(get_money_query(area, until, till, True))),
        "checkout": sa_query_result_to_dict(db.session.execute(get_money_query(area, until, till, False)))
    }), 200


def get_telephones():
    phone_pattern = r'[\+]?[78][\-]?[\d]{3}[\-]?[\d]{3}[\-]?[\d]{2}[\-]?[\d]{2}'
    guests = Guest.query.all()
    result = [guest.telephone for guest in guests if re.fullmatch(phone_pattern, guest.telephone)]

    return jsonify({'data': result}), 200
