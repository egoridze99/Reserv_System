from flask import Blueprint
from flask_jwt_extended import jwt_required

import domains.money.handlers
from decorators import check_user_status

money_blueprint = Blueprint('money_blueprint', __name__)


@money_blueprint.route('')
@jwt_required
@check_user_status
def get_money():
    return handlers.get_money()
