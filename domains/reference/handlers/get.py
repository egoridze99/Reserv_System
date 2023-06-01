from flask import jsonify

from models import Cinema


def get_cinemas():
    cinemas = Cinema.query.all()
    return jsonify([Cinema.to_json(cinema) for cinema in cinemas])
