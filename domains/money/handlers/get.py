from flask import request

from models import Money


def get_money():
    date = request.args.get("date")
    cinema_id = request.args.get("cinema_id")

    money_record = Money.query.filter(Money.date == date).filter(Money.cinema_id == cinema_id).first()

    if money_record is not None:
        return Money.to_json(money_record), 200

    return "", 204
