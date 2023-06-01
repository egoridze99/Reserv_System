from flask import jsonify, request, json
from flask_jwt_extended import get_jwt_identity

from models import EmployeeRoleEnum, Certificate, Guest


def get_certificates():
    identity = get_jwt_identity()
    role = identity["role"]

    if EmployeeRoleEnum[role] != EmployeeRoleEnum.root:
        return jsonify({"msg": "Только администратор может просматривать все сертификаты. Выполните поиск по id или "
                               "номеру телефона"}), 403

    return jsonify([Certificate.to_json(certificate) for certificate in Certificate.query.all()])


def get_certificate_by_ident(ident: str):
    certificate = Certificate.query.filter(Certificate.ident == ident).first()

    if not certificate:
        return jsonify({"msg": "Сертификат не найден"}), 404

    return jsonify(Certificate.to_json(certificate)), 200


def search_certificates():
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

    return jsonify([Certificate.to_json(certificate) for certificate in certificates]), 200
