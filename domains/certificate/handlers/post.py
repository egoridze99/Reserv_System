from datetime import datetime

from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from db import db
from models import User, Guest, Cinema, Certificate
from utils.parse_json import parse_json


def create_certificate():
    data = parse_json(request.data)

    author = User.query.filter(User.id == get_jwt_identity()["id"]).first()
    guest = Guest.query.filter(Guest.id == data["contact"]).first()
    cinema = Cinema.query.filter(Cinema.id == data["cinema_id"]).first()

    if guest is None:
        return {"msg": "Пользователь не найден"}, 400

    certificate = Certificate(
        sum=data["sum"],
        service=data["service"],
        note=data["note"],
        author=author,
        contact=guest,
        cinema=cinema
    )

    db.session.add(certificate)

    try:
        db.session.commit()
        return jsonify(Certificate.to_json(certificate)), 201
    except:
        return jsonify({"msg": "Ошибка при оформлении сертификата"}), 502
