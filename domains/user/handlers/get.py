from flask import jsonify

from models import User, UserStatusEnum


def get_users():
    users = User.query.filter(User.status != UserStatusEnum.deprecated).all()

    return jsonify([User.to_json(user) for user in users]), 200
