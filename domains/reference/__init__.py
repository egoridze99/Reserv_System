from flask import Blueprint
from flask_jwt_extended import jwt_required
import domains.reference.handlers
from decorators import check_user_status

references_blueprint = Blueprint('references_blueprint', __name__)


@references_blueprint.route('/cinemas')
@jwt_required
@check_user_status
def get_cinemas():
    return handlers.get_cinemas()
