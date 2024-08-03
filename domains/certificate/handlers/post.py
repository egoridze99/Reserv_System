from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from db import db
from models import User, Guest, Cinema, Certificate
from utils.parse_json import parse_json
from utils.transactions.create_transaction import create_transaction


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

    transactions = data["transactions"]
    transaction_models = []
    for transaction in transactions:
        transaction_model = create_transaction(cinema,
                                               transaction["transaction_type"],
                                               transaction["sum"],
                                               f"Оплата сертификата {certificate.ident}",
                                               author.id)

        transaction_models.append(transaction_model)

    certificate.transactions = transaction_models

    db.session.add(certificate)

    try:
        db.session.commit()
        return jsonify(Certificate.to_json(certificate)), 201
    except:
        return jsonify({"msg": "Ошибка при оформлении сертификата"}), 502
