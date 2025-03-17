from flask import request

from db import db
from models import Guest
from utils.parse_date import parse_date
from utils.parse_json import parse_json


def create_customer():
    data = parse_json(request.data)

    if Guest.query.filter(Guest.telephone == data['telephone']).first() is not None:
        return {"msg": "Пользователь с таким номером телефона уже есть в системе"}, 400

    if data["telephone"] is None or data["name"] is None:
        return {"msg": "Имя и номер телефона обязательные аттрибуты"}, 400

    customer = Guest(name=data["name"], telephone=data["telephone"])

    optional_fields = ["surname",
                       "patronymic",
                       "birthday_date",
                       "birthplace",
                       "passport_issued_by",
                       "passport_issue_date",
                       "department_code",
                       "passport_identity",
                       "gender"
                       ]

    if data["birthday_date"] is not None:
        data["birthday_date"] = parse_date(data["birthday_date"])

    if data["passport_issue_date"] is not None:
        data["passport_issue_date"] = parse_date(data["passport_issue_date"])

    for field in optional_fields:
        if data[field] is not None:
            setattr(customer, field, data[field])

    db.session.add(customer)

    try:
        db.session.commit()
        return Guest.to_json(customer), 201
    except:
        return {"msg": "Ошибка при создании пользователя"}, 400
