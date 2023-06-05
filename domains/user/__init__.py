from flask import Blueprint
from flask_jwt_extended import jwt_required

from decorators import check_user_status, requires_admin

from domains.user import handlers

user_blueprint = Blueprint('user_blueprint', __name__)


@user_blueprint.route('')
@jwt_required
@check_user_status
@requires_admin
def get_users():
    return handlers.get_users()


@user_blueprint.route('', methods=['POST'])
@jwt_required
@check_user_status
@requires_admin
def register_user():
    return handlers.register_user()


@user_blueprint.route('/<id>', methods=["DELETE"])
@jwt_required
@check_user_status
@requires_admin
def remove_user(id):
    return handlers.remove_user(id)