from datetime import datetime

from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from db import db
from models import User, Guest, Cinema, Certificate
from utils.count_money import count_money
from utils.parse_json import parse_json


def create_certificate():
    data = parse_json(request.data)

    author = User.query.filter(User.id == get_jwt_identity()["id"]).first()
    guest = Guest.query.filter(Guest.telephone == data["telephone"]).first()
    cinema = Cinema.query.filter(Cinema.id == data["cinema_id"]).first()

    if data["card"] + data["cash"] < data["sum"]:
        return jsonify({"msg": "Оплата по карте и наличкой меньше, чем сумма сертификата"}), 400

    if guest is None:
        guest = Guest(name=data['contact'], telephone=data['telephone'])
        db.session.add(guest)

    certificate = Certificate(
        created_at=datetime.today().strftime("%d-%m-%Y %H:%M"),
        sum=data["sum"],
        cash=data["cash"],
        card=data["card"],
        service=data["service"],
        note=data["note"],
        author=author,
        contact=guest,
        cinema=cinema
    )

    money = count_money(datetime.today().date(),
                        data['cinema_id'],
                        certificate.sum,
                        certificate.cash,
                        certificate.card
                        )

    db.session.add(certificate)
    db.session.add(money)

    try:
        db.session.commit()
        return jsonify(Certificate.to_json(certificate)), 201
    except:
        return jsonify({"msg": "Ошибка при оформлении сертификата"}), 502
