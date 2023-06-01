from flask import Blueprint
from flask_jwt_extended import jwt_required

import domains.reservation.handlers

reservations_blueprint = Blueprint('reservations_blueprint', __name__)


# GET
@reservations_blueprint.route('')
@jwt_required
def get_reservations():
    return handlers.get_reservations()


@reservations_blueprint.route('/search')
@jwt_required
def search_reservations():
    return handlers.search_reservations()


# PUT
@reservations_blueprint.route('/<reservation_id>', methods=['PUT'])
@jwt_required
def update_reservation(reservation_id: str):
    return handlers.update_reservation(reservation_id)


# POST
@reservations_blueprint.route('', methods=['POST'])
@jwt_required
def create_reservation():
    return handlers.create_reservation()
