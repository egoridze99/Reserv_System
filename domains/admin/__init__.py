from flask import Blueprint
from flask_jwt_extended import jwt_required

import domains.admin.handlers

admin_blueprint = Blueprint('admin_blueprint', __name__)


@admin_blueprint.route("/common")
@jwt_required
def get_common_info():
    return handlers.get_common_info()


@admin_blueprint.route("/telephones")
@jwt_required
def get_telephones():
    return handlers.get_telephones()


@admin_blueprint.route("/logs/<reservation_id>")
@jwt_required
def get_logs(reservation_id):
    return handlers.get_logs(reservation_id)
