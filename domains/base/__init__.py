from flask import Blueprint
from flask_jwt_extended import jwt_required

import domains.base.handlers
from decorators import check_user_status

base_blueprint = Blueprint('base_blueprint', __name__)


# POST
@base_blueprint.route('/login', methods=["POST"])
def login():
    return handlers.login()
