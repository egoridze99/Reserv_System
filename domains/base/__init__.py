from flask import Blueprint
from flask_jwt_extended import jwt_required

import domains.base.handlers
from decorators import check_user_status

base_blueprint = Blueprint('base_blueprint', __name__)


@base_blueprint.route('/me')
@jwt_required
@check_user_status
def get_me():
    return handlers.get_me()


# POST
@base_blueprint.route('/login', methods=["POST"])
def login():
    return handlers.login()
