from flask import Blueprint
from flask_jwt_extended import jwt_required
from decorators import check_user_status

from domains.transactions import handlers

transactions_blueprint = Blueprint('transactions_blueprint', __name__)


# GET
@transactions_blueprint.route('/reservation/<id>')
@jwt_required
@check_user_status
def get_reservation_transactions(id):
    id = int(id)

    return handlers.get_reservation_transactions(id)


@transactions_blueprint.route('/certificate/<id>')
@jwt_required
@check_user_status
def get_certificate_transactions(id):
    id = int(id)

    return handlers.get_certificate_transactions(id)


@transactions_blueprint.route('/cinema/<cinema_id>')
@jwt_required
@check_user_status
def get_cinema_transactions(cinema_id):
    cinema_id = int(cinema_id)

    return handlers.get_cinema_transactions(cinema_id)


# POST

@transactions_blueprint.route('', methods=['POST'])
@jwt_required
@check_user_status
def create_transaction():
    return handlers.create_transaction()


@transactions_blueprint.route('/refund/<id>', methods=['POST'])
@jwt_required
@check_user_status
def make_refund(id: str):
    return handlers.make_refund(id)


@transactions_blueprint.route('/id', methods=['POST'])
@jwt_required
@check_user_status
def generate_transaction_id():
    return handlers.generate_transaction_id()
