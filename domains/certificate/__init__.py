from flask import Blueprint
from flask_jwt_extended import jwt_required

import domains.certificate.handlers
from decorators import check_user_status

certificate_blueprint = Blueprint('certificate_blueprint', __name__)


# GET
@certificate_blueprint.route('')
@jwt_required
@check_user_status
def get_certificates():
    return handlers.get_certificates()


@certificate_blueprint.route('/<ident>')
@jwt_required
@check_user_status
def get_certificate_by_ident(ident: str):
    return handlers.get_certificate_by_ident(ident)


@certificate_blueprint.route('/search')
@jwt_required
@check_user_status
def search_certificates():
    return handlers.search_certificates()


# POST
@certificate_blueprint.route('', methods=['POST'])
@jwt_required
@check_user_status
def create_certificate():
    return handlers.create_certificate()
