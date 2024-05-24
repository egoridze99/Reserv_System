from sqlalchemy.orm import backref

from models.abstract import AbstractBaseModel
from db import db
from models.dictionaries import queue_room


class Room(AbstractBaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), nullable=False)
    cinema_id = db.Column(db.Integer, db.ForeignKey('cinema.id', name="cinema_id"))

    cinema = db.relationship("Cinema", backref=backref("rooms", uselist=True))
    queue = db.relationship('ReservationQueue', secondary=queue_room)

    def __str__(self):
        return "<Зал id = {} название = {}>".format(self.id, self.name)

    @staticmethod
    def to_json(room: 'Room'):
        return {"id": room.id, "name": room.name}
