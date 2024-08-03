from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from db import db
from models import Transaction, Reservation, Cinema
from services.sbp_service import *
from typings import UserJwtIdentity
from utils.parse_json import parse_json
from utils.transactions.create_transaction import create_transaction as create_transaction_model
from utils.transactions.make_refund import make_refund as make_refund_global


def make_refund(id: str):
    identity: 'UserJwtIdentity' = get_jwt_identity()

    transaction: "Transaction" = Transaction.query.filter_by(id=id).first()

    if not transaction:
        return jsonify({"msg": "Транзакция не найдена"}), 400

    try:
        transaction, log = make_refund_global(transaction, identity["name"])
    except SbpServiceException as e:
        return jsonify({"msg": str(e)}), 400

    try:
        db.session.add(transaction)
        if log:
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

    try:
        transaction = create_transaction_model(
            cinema,
            data["transaction_type"],
            data["sum"],
            data["description"],
            identity["id"]
        )
    except SbpServiceException as e:
        return jsonify({"msg": str(e)}), 400

    if reservation:
        reservation.transactions.append(transaction)
        db.session.add(reservation)
    else:
        db.session.add(transaction)

    try:
        db.session.commit()
        return jsonify(Transaction.to_json(transaction)), 201
    except Exception as e:
        print(e)

        return jsonify({"msg": "Ошибка при добавлении транзакции"}), 400


def generate_transaction_id():
    return Transaction.generate_id()
