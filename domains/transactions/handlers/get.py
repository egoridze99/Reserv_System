from flask import jsonify, request
from sqlalchemy import func, text

from models import Reservation, Transaction, Certificate, Cinema, City
from models.dictionaries import reservation_transaction_dict, certificate_transaction_dict
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
    transactions = Transaction \
        .query \
        .join(Cinema) \
        .join(City) \
        .outerjoin(reservation_transaction_dict, Transaction.id == reservation_transaction_dict.c.transaction_id) \
        .outerjoin(Reservation, reservation_transaction_dict.c.reservation_id == Reservation.id) \
        .filter((Transaction.cinema_id == cinema_id)) \
        .filter(text("""date(get_shift_date("transaction".created_at, city.timezone, 0)) = :target""")).params(
        target=date) \
        .filter(
        text(
            """iif(
                get_shift_date(
                reservation.date, 
                city.timezone, 
                reservation.duration),
                date(
                    get_shift_date(
                        reservation.date, 
                        city.timezone, 
                        reservation.duration)) != :given_date, true)""")).params(
        given_date=date) \
        .all()

    return jsonify([Transaction.to_json(transaction) for transaction in transactions]), 200
