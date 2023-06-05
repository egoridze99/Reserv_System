from flask import Blueprint
from flask_jwt_extended import jwt_required

import domains.queue.handlers
from decorators import check_user_status

queue_blueprint = Blueprint('queue_blueprint', __name__)


# GET
@queue_blueprint.route('')
@jwt_required
@check_user_status
def get_queue():
    return handlers.get_queue()


# POST
@queue_blueprint.route('', methods=['POST'])
@jwt_required
@check_user_status
def create_reservation_in_queue():
    return handlers.create_reservation_in_queue()
