import hashlib
from datetime import timedelta

from flask import request, jsonify, json
from flask_jwt_extended import create_access_token, get_jwt_identity

from db import db
from models import User, EmployeeRoleEnum
from utils.parse_json import parse_json


def register_user():
    identity = get_jwt_identity()
    role = identity["role"]

    if EmployeeRoleEnum[role] != EmployeeRoleEnum.root:
        return {"message": "Недостаточно прав"}, 403

    username = request.json.get("login")
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
    user = User(login=username, password=password, name=name, surname=surname, role=EmployeeRoleEnum[role].value)

    db.session.add(user)
    try:
        db.session.commit()
        return {"message": "ok"}, 200
    except Exception:
        return {"message": "error"}, 400


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

    user = User.query.filter(User.login == username).first()

    if not user:
        return jsonify({"msg": "Неверный логин"}), 400

    password = hashlib.md5(password.encode()).hexdigest()

    if password != user.password:
        return jsonify({"msg": "Неверный пароль"}), 400

    jwt = create_access_token(identity={
        "id": user.id,
        "login": username,
        "role": user.role.value,
        "name": f"{user.name} {user.surname}"
    }, expires_delta=timedelta(hours=6))

    return jsonify({"jwt": jwt}), 200
