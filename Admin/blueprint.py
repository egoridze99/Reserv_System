import hashlib
import re

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from Admin.queries import get_checkout_query, get_duration_query, get_money_query
from models import *

from app import db
from utils.sa_query_result_to_dict import sa_query_result_to_dict

admin_blueprint = Blueprint('admin_blueprint', __name__)


@admin_blueprint.route('/login', methods=["POST"])
def index():
    if not request.is_json:
        return jsonify({"msg": "Ошибка сервера"}), 400

    login = request.json.get('login', None)
    password = request.json.get('password', None)

    print(request.json.get('login', None))

    if not login:
        return jsonify({"msg": "Не введен логин"}), 400
    if not password:
        return jsonify({"msg": "Не введен пароль"}), 400

    user = User.query.filter(User.login == login).first()

    if not user:
        return jsonify({"msg": "Неверный логин"}), 400

    password = hashlib.md5(password.encode()).hexdigest()

    if password != user.password:
        return jsonify({"msg": "Неверный пароль"}), 400

    jwt = create_access_token(identity={
        "id": user.id,
        "login": login,
        "role": user.role.value,
        "name": f"{user.name} {user.surname}"
    }, expires_delta=timedelta(hours=6))

    return {"jwt": jwt}, 200


@admin_blueprint.route("/common")
@jwt_required
def get_common_info():
    identity = get_jwt_identity()
    role = identity["role"]

    if EmployeeRoleEnum[role] != EmployeeRoleEnum.root:
        return {"message": "Недостаточно прав"}, 403

    untill = request.args.get('untill')
    till = request.args.get('till')
    area = request.args.get('area')

    return jsonify({
        "duration": sa_query_result_to_dict(db.session.execute(get_duration_query(area, untill, till))),
        "money": sa_query_result_to_dict(db.session.execute(get_money_query(area, untill, till))),
        "checkout": sa_query_result_to_dict(db.session.execute(get_checkout_query(area, untill, till)))
    }), 200


@admin_blueprint.route("/new_user", methods=["POST"])
@jwt_required
def new_user():
    identity = get_jwt_identity()
    role = identity["role"]

    if EmployeeRoleEnum[role] != EmployeeRoleEnum.root:
        return {"message": "Недостаточно прав"}, 403

    login = request.json.get("login")
    password = request.json.get("password")
    name = request.json.get("name")
    surname = request.json.get("surname")
    role = request.json.get("role")

    user = User.query.filter(User.login == login).first()

    if not login:
        return {"msg": "Логин пустой"}, 400

    if not password:
        return {"msg": "Пароль пустой"}, 400

    if not name:
        return {"msg": "Имя пустое"}, 400

    if not surname:
        return {"msg": "Фамилия пустая"}, 400

    if user:
        return {"msg": "Такой пользователь уже есть"}, 400

    password = hashlib.md5(password.encode()).hexdigest()
    user = User(login=login, password=password, name=name, surname=surname, role=EmployeeRoleEnum[role].value)

    db.session.add(user)
    try:
        db.session.commit()
        return {"message": "ok"}, 200
    except Exception:
        return {"message": "error"}, 400


@admin_blueprint.route("/telephones")
@jwt_required
def get_telephones():
    phone_pattern = r'[\+]?[78][\-]?[\d]{3}[\-]?[\d]{3}[\-]?[\d]{2}[\-]?[\d]{2}'
    guests = Guest.query.all()
    result = [guest.telephone for guest in guests if re.fullmatch(phone_pattern, guest.telephone)]

    return jsonify({'data': result}), 200


@admin_blueprint.route("/logs/<reservation_id>")
@jwt_required
def get_logs(reservation_id):
    logs = UpdateLogs.query.filter(UpdateLogs.reservation_id == reservation_id).all()
    logs = [log.toJson() for log in logs]
    logs.sort(key=lambda x: datetime.strptime(x['created_at'], '%d-%m-%Y %H:%M:%S'))
    return jsonify(logs)
