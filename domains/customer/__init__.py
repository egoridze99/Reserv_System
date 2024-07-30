from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from decorators import check_user_status, requires_admin
from domains.customer import handlers

customer_blueprint = Blueprint('customer_blueprint', __name__)


@customer_blueprint.route('')
@jwt_required
@check_user_status
def get_users():
    args = request.args
    telephone = args.get('telephone')

    return handlers.get_customer(telephone)


@customer_blueprint.route('/id')
@jwt_required
@check_user_status
def get_users_by_id():
    args = request.args
    ids = args.get('ids')

    if not ids:
        return jsonify([]), 200

    ids = list(map(int, ids.split(',')))

    return handlers.get_customer_by_id(ids)


@customer_blueprint.route('/comments/<id>')
@jwt_required
@check_user_status
def get_comments(id):
    if id is None:
        return {"msg": "id посетителя некорректен"}

    return handlers.get_customer_comments(int(id))


@customer_blueprint.route('/logs')
@jwt_required
@check_user_status
def get_logs():
    args = request.args
    customer_id = int(args.get('customer_id'))

    return handlers.get_logs(customer_id)


@customer_blueprint.route('', methods=['POST'])
@jwt_required
@check_user_status
def add_customer():
    return handlers.create_customer()


@customer_blueprint.route('/<id>', methods=['PUT'])
@jwt_required
@check_user_status
def edit_customer(id: str):
    id = int(id)
    return handlers.edit_customer(id)


@customer_blueprint.route('/comments', methods=['PUT'])
@jwt_required
@check_user_status
def add_comment():
    return handlers.add_comment_to_customer()
