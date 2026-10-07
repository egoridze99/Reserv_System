from flask import request, jsonify

from services import cashier_service
from utils.parse_date import parse_date


def get_money():
    date = parse_date(request.args.get("date"))
    cinema_id = request.args.get("cinema_id")

    return jsonify(cashier_service.get_cashier_info(date, cinema_id)), 0
