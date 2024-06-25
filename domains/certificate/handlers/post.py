from datetime import datetime

from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from db import db
from models import User, Guest, Cinema, Certificate, Transaction, TransactionTypeEnum, TransactionStatusEnum
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

    transactions = data["transactions"]
    transaction_models = []
    for transaction in transactions:
        status = TransactionStatusEnum.completed if TransactionTypeEnum[
                                                        transaction[
                                                            "transaction_type"]] != TransactionTypeEnum.sbp else TransactionStatusEnum.pending

        transaction_model = Transaction(
            created_at=datetime.now(),
            sum=transaction["sum"],
            description=f"Оплата сертификата {certificate.ident}",
            transaction_type=transaction["transaction_type"],
            transaction_status=status,
            cinema=cinema,
            author=author
        )

        transaction_models.append(transaction_model)

    certificate.transactions = transaction_models

    db.session.add(certificate)

    try:
        db.session.commit()
        return jsonify(Certificate.to_json(certificate)), 201
    except:
        return jsonify({"msg": "Ошибка при оформлении сертификата"}), 502
