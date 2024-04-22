import json

from flask import request
from flask_jwt_extended import get_jwt_identity

from db import db
from models import Guest, GuestComment, User, GuestChangesLogs, GenderEnum
from typings import UserJwtIdentity
from utils.parse_date import parse_date
from utils.parse_json import parse_json


def edit_customer(id: int):
    identity: 'UserJwtIdentity' = get_jwt_identity()
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

    if data["gender"] is not None:
        data["gender"] = GenderEnum.М if data["gender"] == "М" else GenderEnum.Ж

    old_values = json.dumps(Guest.to_json(customer))
    for key in data:
        setattr(customer, key, data[key])
    new_values = json.dumps(Guest.to_json(customer))

    log = GuestChangesLogs(guest_id=customer.id,
                           author=identity["name"], new=new_values, old=old_values)

    db.session.add(log)
    db.session.add(customer)

    try:
        db.session.commit()
        return Guest.to_json(customer), 200
    except:
        return {"msg": "Ошибка при редактировании пользователя"}, 400


def add_comment_to_customer():
    identity: UserJwtIdentity = get_jwt_identity()
    data = parse_json(request.data)

    customer = Guest.query.filter(Guest.id == data["customer_id"]).first()

    if customer is None:
        return {"msg": "Посетитель не найден"}, 400

    author = User.query.filter(User.id == identity["id"]).first()

    comment = GuestComment(text=data["comment"], author=author)
    customer.comments.append(comment)

    try:
        db.session.add(customer)
        db.session.commit()
        return GuestComment.to_json(comment), 201
    except:
        return {"msg": "Ошибка при добавлении коммента пользователю"}, 400
