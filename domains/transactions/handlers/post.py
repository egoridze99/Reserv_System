import json
from datetime import datetime

from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from db import db
from domains.transactions.handlers.utils.dump_transaction_to_json import dump_transaction_to_json
from models import Transaction, Reservation, TransactionTypeEnum, TransactionStatusEnum, Cinema, TransactionChangesLog
from typings import UserJwtIdentity
from utils.parse_json import parse_json


def make_refund(id: str):
    identity: 'UserJwtIdentity' = get_jwt_identity()

    transaction = Transaction.query.filter_by(id=id).first()

    if not transaction:
        return jsonify({"msg": "Транзакция не найдена"}), 400

    old_values = json.dumps(dump_transaction_to_json(transaction))
    transaction.transaction_status = TransactionStatusEnum.refunded
    new_values = json.dumps(dump_transaction_to_json(transaction))

    log = TransactionChangesLog(transaction_id=transaction.id,
                                author=identity["name"], new=new_values, old=old_values)

    try:
        db.session.add(transaction)
        db.session.add(log)
        db.session.commit()
        return jsonify({"msg": "ok"}), 200
    except:
        return jsonify({"msg": "Произошла непредвиденная ошибка"}), 400


def create_transaction():
    identity: UserJwtIdentity = get_jwt_identity()
    data = parse_json(request.data)

    reservation_id = None
    if 'reservation_id' in data:
        reservation_id = data['reservation_id']

    reservation: 'Reservation' or None = None
    if reservation_id:
        reservation = Reservation.query.filter(Reservation.id == reservation_id).first()

    if 'cinema_id' in data:
        cinema_id = data['cinema_id']
    else:
        cinema_id = reservation.room.cinema.id

    cinema = Cinema.query.filter(Cinema.id == cinema_id).first()

    transaction_status = TransactionStatusEnum.pending
    if TransactionTypeEnum[data["transaction_type"]] != TransactionTypeEnum.sbp:
        transaction_status = TransactionStatusEnum.completed

    transaction = Transaction(
        sum=data['sum'],
        created_at=datetime.now(),
        description=data['description'],
        cinema=cinema,
        author_id=identity["id"],
        transaction_type=data['transaction_type'],
        transaction_status=transaction_status,
    )

    if reservation:
        reservation.transactions.append(transaction)
        db.session.add(reservation)
    else:
        db.session.add(transaction)

    try:
        db.session.commit()
        return jsonify(Transaction.to_json(transaction)), 201
    except:
        return jsonify({"msg": "Ошибка при добавлении транзакции"}), 400


def generate_transaction_id():
    return Transaction.generate_id()
