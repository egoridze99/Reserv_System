import hashlib

from flask import request

from db import db
from models import EmployeeRoleEnum, User, UserStatusEnum


def register_user():
    username = request.json.get("login")
    password = request.json.get("password")
    name = request.json.get("name")
    surname = request.json.get("surname")
    role = request.json.get("role")

    user: "User" or None = User.query.filter(User.login == username).first()

    if not username:
        return {"msg": "Логин пустой"}, 400

    if not password:
        return {"msg": "Пароль пустой"}, 400

    if not name:
        return {"msg": "Имя пустое"}, 400

    if not surname:
        return {"msg": "Фамилия пустая"}, 400

    if user and user.status != UserStatusEnum.deprecated:
        return {"msg": "Такой пользователь уже есть"}, 400

    password = hashlib.md5(password.encode()).hexdigest()
    user = User(login=username, password=password, name=name, surname=surname, role=EmployeeRoleEnum[role].value)

    db.session.add(user)
    try:
        db.session.commit()
        return {"message": "ok"}, 200
    except Exception:
        return {"message": "error"}, 400
