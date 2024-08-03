from flask import jsonify
from flask_jwt_extended import get_jwt_identity

from models import User


def get_me():
    user = User.query.filter(User.id == get_jwt_identity()["id"]).first()

    return jsonify(User.to_json(user)), 200
