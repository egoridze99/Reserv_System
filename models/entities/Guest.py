from models.abstract import AbstractBaseModel
from db import db


class Guest(AbstractBaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String(40), nullable=False)
    telephone = db.Column(db.String(30), nullable=False)

    surname = db.Column(db.String(100), nullable=True)
    patronymic = db.Column(db.String(100), nullable=True)
    birthday_date = db.Column(db.Date, nullable=True)
    birthplace = db.Column(db.String(100), nullable=True)
    passport_issued_by = db.Column(db.String(100), nullable=True)
    passport_issue_date = db.Column(db.Date, nullable=True)
    department_code = db.Column(db.String(10), nullable=True)
    passport_identity = db.Column(db.String(12), nullable=True)

    reservation = db.relationship("Reservation", backref='guest')
    certificate = db.relationship("Certificate", backref='contact')
    queue = db.relationship("ReservationQueue", backref='contact')

    def __str__(self):
        return "<Гость id = {} Имя = {} Номер = {}>".format(self.id, self.name, self.telephone)

    @staticmethod
    def to_json(guest: 'Guest'):
        return {
            "id": guest.id,
            "name": guest.name,
            "telephone": guest.telephone
        }
