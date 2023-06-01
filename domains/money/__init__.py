from flask import Blueprint
from flask_jwt_extended import jwt_required

import domains.money.handlers

money_blueprint = Blueprint('money_blueprint', __name__)


@money_blueprint.route('')
@jwt_required
def get_money():
    return handlers.get_money()
