from sqlalchemy.orm import backref

from models.abstract import AbstractBaseModel
from db import db
from models.entities.buisness.Room import Room


class Cinema(AbstractBaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), nullable=False)

    sbp_terminal_id = db.Column(db.String, db.ForeignKey('sbp_terminal.id'))
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))

    sbp_terminal = db.relationship("SbpTerminal", backref=backref("cinema", uselist=False))
    city = db.relationship("City", backref=backref("cinemas", uselist=True))

    closed = db.Column(db.Boolean, default=False)

    def __str__(self):
        return "<Кинотеатр id={} адрес={}>".format(self.id, self.name)

    @staticmethod
    def to_json(cinema: 'Cinema') -> dict:
        return {
            "id": cinema.id,
            "name": cinema.name,
            "rooms": [Room.to_json(room) for room in cinema.rooms],

            "sbp_terminal": cinema.sbp_terminal.id if cinema.sbp_terminal else None
        }
