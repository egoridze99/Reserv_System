from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from Schedule.utils import count_money
from models import *
from utils.parse_json import parse_json

certificate_blueprint = Blueprint('certificate_blueprint', __name__)


@certificate_blueprint.route('/certificate')
@jwt_required
def get_certificates():
    identity = get_jwt_identity()
    role = identity["role"]

    if EmployeeRoleEnum[role] != EmployeeRoleEnum.root:
        return jsonify({"msg": "Только администратор может просматривать все сертификаты. Выполните поиск по id или "
                               "номеру телефона"}), 403

    return jsonify([Certificate.toJson(certificate) for certificate in Certificate.query.all()])


@certificate_blueprint.route('/certificate/<ident>')
@jwt_required
def get_certificate_by_ident(ident: str):
    certificate = Certificate.query.filter(Certificate.ident == ident).first()

    if not certificate:
        return jsonify({"msg": "Сертификат не найден"}), 404

    return jsonify(Certificate.toJson(certificate)), 200


@certificate_blueprint.route('/certificate/search')
@jwt_required
def get_certificate():
    ids: list[str] = request.args.get('ids')
    telephones: list[str] = request.args.get('telephones')

    certificate_query = Certificate.query.join(Guest)

    if ids:
        ids = json.loads(ids)
        certificate_query = certificate_query.filter(Certificate.ident.in_(ids))

    if telephones:
        telephones = json.loads(telephones)
        certificate_query = certificate_query.filter(Guest.telephone.in_(telephones))

    certificates = certificate_query.all()

    return jsonify([Certificate.toJson(certificate) for certificate in certificates]), 200


@certificate_blueprint.route('/certificate', methods=['POST'])
@jwt_required
def create_certificate():
    data = parse_json(request.data)

    author = User.query.filter(User.id == get_jwt_identity()["id"]).first()
    guest = Guest.query.filter(Guest.telephone == data["telephone"]).first()

    if guest is None:
        guest = Guest(name=data['contact'], telephone=data['telephone'])
        db.session.add(guest)

    certificate = Certificate(
        created_at=datetime.today().strftime("%d-%m-%Y"),
        sum=data["sum"],
        cash=data["cash"],
        card=data["card"],
        service=data["service"],
        note=data["note"],
        author=author,
        contact=guest
    )

    money = count_money(datetime.today().date(),
                        data['cinema_id'],
                        certificate.sum,
                        certificate.cash,
                        certificate.card
                        )

    db.session.add(certificate)
    db.session.add(money)

    try:
        db.session.commit()
        return jsonify(Certificate.toJson(certificate)), 201
    except:
        return jsonify({"msg": "Ошибка при оформлении сертификата"}), 502
