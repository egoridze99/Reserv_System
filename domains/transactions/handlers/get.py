from datetime import datetime, time, timedelta

from flask import jsonify, request
from sqlalchemy import text, or_, func, cast, String, not_, and_
from sqlalchemy.orm import aliased
from sqlalchemy.sql import exists

from db import db
from models import Reservation, Transaction, Certificate, Cinema, City, TransactionChangesLog
from models.dictionaries import reservation_transaction_dict
from utils.convert_tz import convert_tz
from utils.parse_date import parse_date


def get_reservation_transactions(id: int):
    reservation: 'Reservation' = Reservation.query.filter(Reservation.id == id).first()
    transactions = reservation.transactions

    return jsonify([Transaction.to_json(transaction) for transaction in transactions]), 200


def get_certificate_transactions(id: int):
    certificate: 'Certificate' = Certificate.query.filter(Certificate.id == id).first()
    transactions = certificate.transactions

    return jsonify([Transaction.to_json(transaction) for transaction in transactions]), 200


def get_cinema_transactions(cinema_id: int):
    date = parse_date(request.args.get("date"))

    cinema = Cinema.query.filter(Cinema.id == cinema_id).first()
    min_date = convert_tz(datetime.combine(date, time(8)), cinema.city.timezone, True)
    max_date = convert_tz(datetime.combine(date + timedelta(days=1), time(8)), cinema.city.timezone, True)

    transaction_log_alias = aliased(TransactionChangesLog, name="transaction_log_alias")
    subquery = (
        db.session.query(transaction_log_alias.transaction_id.label("transaction_id"))
        .filter(transaction_log_alias.created_at.between(min_date, max_date))
        .subquery(name="transaction_log_subquery")
    )

    transactions = Transaction \
        .query \
        .join(Cinema) \
        .join(City) \
        .outerjoin(reservation_transaction_dict, Transaction.id == reservation_transaction_dict.c.transaction_id) \
        .outerjoin(Reservation, reservation_transaction_dict.c.reservation_id == Reservation.id) \
        .filter((Transaction.cinema_id == cinema_id)) \
        .filter(or_(Transaction.created_at.between(min_date, max_date), Transaction.id.in_(subquery))) \
        .params(target=date) \
        .filter(func.iif(exists().where(and_(Reservation.id == reservation_transaction_dict.c.reservation_id,
                                             Transaction.id == reservation_transaction_dict.c.transaction_id)).correlate(
        Transaction),
                         not_(
                             func.datetime(Reservation.date,
                                           '+' + cast(Reservation.duration, String) + ' hours').between(min_date,
                                                                                                        max_date)),
                         True)
                ) \
        .all()

    return jsonify([Transaction.to_json(transaction) for transaction in transactions]), 200


def get_logs(transaction_id: str):
    logs = TransactionChangesLog.query.filter(TransactionChangesLog.transaction_id == transaction_id).all()
    logs = [TransactionChangesLog.to_json(log) for log in logs]
    logs.sort(key=lambda x: x['created_at'])

    return jsonify(logs)
