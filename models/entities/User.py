from db import db
from models.abstract import AbstractBaseModel
from models.enums.UserStatusEnum import UserStatusEnum
from models.enums.EmployeeRoleEnum import EmployeeRoleEnum


class User(AbstractBaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login = db.Column(db.String(40), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.Enum(EmployeeRoleEnum), default=EmployeeRoleEnum.admin)
    name = db.Column(db.String(40))
    surname = db.Column(db.String(40))
    status = db.Column(db.Enum(UserStatusEnum), default=UserStatusEnum.active)

    reservation = db.relationship("Reservation", backref='author')
    certificate = db.relationship("Certificate", backref='author')
    queue = db.relationship("ReservationQueue", backref='author')

    @staticmethod
    def to_json(user: 'User'):
        return {
            "id": user.id,
            "login": user.login,
            "role": user.role.name,
            "status": user.status.name,
            "name": user.name,
            "surname": user.surname,
            "fullname": f"{user.name} {user.surname}"
        }
