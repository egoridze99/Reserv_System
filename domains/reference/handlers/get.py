from flask import jsonify

from db import db
from models import Cinema, City


def get_cinemas():
    cinemas = Cinema.query.all()
    return jsonify([Cinema.to_json(cinema) for cinema in cinemas])


def get_cities():
    cities = db.session.query(City.id, City.name, City.timezone).select_from(Cinema).join(City,
                                                                                          City.id == Cinema.city_id).group_by(
        City.id).all()

    return jsonify([City.to_json(city) for city in cities])


def is_authenticated():
    return "ok", 200
