from models.abstract import AbstractBaseModel
from db import db
from models.dictionaries import guest_comment_dict
from models.enums import GenderEnum


class Guest(AbstractBaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String(40), nullable=False)
    telephone = db.Column(db.String(30), nullable=False)

    gender = db.Column(db.Enum(GenderEnum))
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

    comments = db.relationship('GuestComment', secondary=guest_comment_dict, cascade="all, delete")

    def __str__(self):
        return "<Гость id = {} Имя = {} Номер = {}>".format(self.id, self.name, self.telephone)

    @staticmethod
    def to_json(guest: 'Guest'):
        return {
            "id": guest.id,
            "name": guest.name,
            "telephone": guest.telephone,

            "gender": guest.gender.name if guest.gender is not None else None,
            "surname": guest.surname,
            "patronymic": guest.patronymic,
            "birthday_date": guest.birthday_date.strftime("%Y-%m-%d") if guest.birthday_date is not None else None,
            "birthplace": guest.birthplace,
            "passport_issued_by": guest.passport_issued_by,
            "passport_issue_date": guest.passport_issue_date.strftime(
                "%Y-%m-%d") if guest.passport_issue_date is not None else None,
            "department_code": guest.department_code,
            "passport_identity": guest.passport_identity,
        }
