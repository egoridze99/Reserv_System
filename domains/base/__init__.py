from flask import Blueprint
from flask_jwt_extended import jwt_required

import domains.base.handlers

base_blueprint = Blueprint('base_blueprint', __name__)


# POST
@base_blueprint.route('/login', methods=["POST"])
def login():
    return handlers.login()


@base_blueprint.route('/register', methods=['POST'])
@jwt_required
def register_user():
    return handlers.register_user()
