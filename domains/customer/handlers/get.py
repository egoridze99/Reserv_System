from typing import Optional

from flask import jsonify

from models import Guest


def get_customer(telephone: Optional[str]):
    if telephone:
        return jsonify([Guest.to_json(customer) for customer in
                        Guest.query.filter(Guest.telephone.like(f"%{telephone}%")).limit(100).all()])

    return jsonify([Guest.to_json(customer) for customer in Guest.query.limit(100).all()])
