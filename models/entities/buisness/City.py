from db import db
from models.abstract import AbstractBaseModel


class City(AbstractBaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    timezone = db.Column(db.String(50), nullable=False)

    @staticmethod
    def to_json(city):
        return {
            "id": city.id,
            "name": city.name,
            "timezone": city.timezone
        }
