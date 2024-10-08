import hashlib
from datetime import timedelta

from flask import request, jsonify
from flask_jwt_extended import create_access_token
from sqlalchemy import and_

from models import User, UserStatusEnum
from utils.parse_json import parse_json


def login():
    if not request.is_json:
        return jsonify({"msg": "Ошибка сервера"}), 400

    data = parse_json(request.data)

    username = data["login"] or None
    password = data["password"] or None

    if not username:
        return jsonify({"msg": "Не введен логин"}), 400
    if not password:
        return jsonify({"msg": "Не введен пароль"}), 400

    user = User.query.filter(and_(User.login == username, User.status != UserStatusEnum.deprecated)).first()

    if not user:
        return jsonify({"msg": "Неверный логин"}), 400

    password = hashlib.md5(password.encode()).hexdigest()

    if password != user.password:
        return jsonify({"msg": "Неверный пароль"}), 400

    jwt = create_access_token(identity={
        "id": user.id,
        "login": username,
        "role": user.role.value,
        "name": f"{user.name} {user.surname}",
        "status": user.status.value
    }, expires_delta=timedelta(hours=6))

    return jsonify({"jwt": jwt}), 200
