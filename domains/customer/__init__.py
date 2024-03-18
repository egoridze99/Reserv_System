from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from decorators import check_user_status, requires_admin
from domains.customer import handlers

customer_blueprint = Blueprint('customer_blueprint', __name__)


@customer_blueprint.route('')
@jwt_required
@check_user_status
def get_users():
    args = request.args
    telephone = args.get('telephone')

    return handlers.get_customer(telephone)
