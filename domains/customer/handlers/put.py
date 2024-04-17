from flask import request

from db import db
from models import Guest
from utils.parse_date import parse_date
from utils.parse_json import parse_json


def edit_customer(id: int):
    data = parse_json(request.data)

    customer = Guest.query.filter(Guest.id == id).first()

    if customer is None:
        return {"msg": "Пользователь не найден в системе"}, 400

    if Guest.query.filter((Guest.telephone == data['telephone']) & (Guest.id != customer.id)).first() is not None:
        return {"msg": "Пользователь с таким номером телефона уже есть в системе"}, 400

    if data["telephone"] is None or data["name"] is None:
        return {"msg": "Имя и номер телефона обязательные аттрибуты"}, 400

    if data["birthday_date"] is not None:
        data["birthday_date"] = parse_date(data["birthday_date"])

    if data["passport_issue_date"] is not None:
        data["passport_issue_date"] = parse_date(data["passport_issue_date"])

    for key in data:
        setattr(customer, key, data[key])

    db.session.add(customer)

    try:
        db.session.commit()
        return Guest.to_json(customer), 200
    except:
        return {"msg": "Ошибка при редактировании пользователя"}, 400
