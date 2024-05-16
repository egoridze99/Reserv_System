import shortuuid
from sqlalchemy import func

from db import db
from models.abstract import AbstractBaseModel
from models.entities.buisness.User import User
from models.entities.buisness.Cinema import Cinema
from models.entities.buisness.Guest import Guest

from models.enums.CertificateStatusEnum import CertificateStatusEnum


class Certificate(AbstractBaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ident = db.Column(db.String(6), unique=True)
    created_at = db.Column(db.DateTime, default=func.localtimestamp())
    author_id = db.Column(db.Integer, db.ForeignKey("user.id", name="author_id"))
    contact_id = db.Column(db.Integer, db.ForeignKey("guest.id", name="contact_id"))
    cinema_id = db.Column(db.Integer, db.ForeignKey('cinema.id', name="cinema_id"))
    status = db.Column(db.Enum(CertificateStatusEnum), default=CertificateStatusEnum.active)
    sum = db.Column(db.Integer, nullable=False)
    service = db.Column(db.String(100), nullable=False)
    note = db.Column(db.Text)

    transactions = db.relationship('Transaction', secondary='certificate_transaction_dict', cascade="all, delete")
    reservation = db.relationship("Reservation", backref='certificate')

    def __init__(cls, **kwargs):
        super().__init__(**kwargs)
        cls.ident = shortuuid.ShortUUID().random(length=6)

    @staticmethod
    def to_json(certificate: 'Certificate'):
        return {
            "id": certificate.id,
            "ident": certificate.ident,

            "created_at": certificate.created_at.strftime('%Y-%m-%dT%H:%M'),
            "status": certificate.status.name,
            "sum": certificate.sum,

            "service": certificate.service,
            "note": certificate.note,

            "author": User.to_json(certificate.author),
            "contact": Guest.to_json(certificate.contact),
            "cinema": Cinema.to_json(certificate.cinema)
        }
