from flask import Blueprint
from flask_jwt_extended import jwt_required

import domains.reservation.handlers
from decorators import check_user_status

reservations_blueprint = Blueprint('reservations_blueprint', __name__)


# GET
@reservations_blueprint.route('')
@jwt_required
@check_user_status
def get_reservations():
    return handlers.get_reservations()


@reservations_blueprint.route('/search')
@jwt_required
@check_user_status
def search_reservations():
    return handlers.search_reservations()


# PUT
@reservations_blueprint.route('/<reservation_id>', methods=['PUT'])
@jwt_required
@check_user_status
def update_reservation(reservation_id: str):
    return handlers.update_reservation(reservation_id)


# POST
@reservations_blueprint.route('', methods=['POST'])
@jwt_required
@check_user_status
def create_reservation():
    return handlers.create_reservation()


@reservations_blueprint.route("/logs/<reservation_id>")
@jwt_required
@check_user_status
def get_logs(reservation_id):
    return handlers.get_logs(reservation_id)