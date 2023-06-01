from flask import Blueprint
from flask_jwt_extended import jwt_required
import domains.reference.handlers

references_blueprint = Blueprint('references_blueprint', __name__)


@references_blueprint.route('/cinemas')
@jwt_required
def get_cinemas():
    return handlers.get_cinemas()
