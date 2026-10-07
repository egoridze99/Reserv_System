from flask import request

from db import db
from models import Guest
from utils.parse_date import parse_date


def prepare_customer_data(data: dict):
    """Проверяет обязательные поля и приводит даты к date. Возвращает ответ с ошибкой или None"""
    if data["telephone"] is None or data["name"] is None:
        return {"msg": "Имя и номер телефона обязательные аттрибуты"}, 400

    for field in ("birthday_date", "passport_issue_date"):
        if data[field] is not None:
            data[field] = parse_date(data[field])


def create_customer():
    data = request.get_json(force=True)

    if Guest.query.filter(Guest.telephone == data['telephone']).first() is not None:
        return {"msg": "Пользователь с таким номером телефона уже есть в системе"}, 400

    error = prepare_customer_data(data)
    if error:
        return error

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

    for field in optional_fields:
        if data[field] is not None:
            setattr(customer, field, data[field])

    db.session.add(customer)

    try:
        db.session.commit()
        return Guest.to_json(customer), 201
    except:
        return {"msg": "Ошибка при создании пользователя"}, 400
