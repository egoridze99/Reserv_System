from flask import Blueprint
from flask_jwt_extended import jwt_required

import domains.admin.handlers
from decorators import check_user_status, requires_admin

admin_blueprint = Blueprint('admin_blueprint', __name__)


@admin_blueprint.route("/common")
@jwt_required
@check_user_status
@requires_admin
def get_common_info():
    return handlers.get_common_info()


@admin_blueprint.route("/telephones")
@jwt_required
@check_user_status
@requires_admin
def get_telephones():
    return handlers.get_telephones()

