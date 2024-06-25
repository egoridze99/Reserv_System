from flask import request, jsonify

from services.cashier_service import CashierService
from utils.parse_date import parse_date


def get_money():
    date = parse_date(request.args.get("date"))
    cinema_id = request.args.get("cinema_id")

    return jsonify(CashierService.get_cashier_info(date, cinema_id)), 0
