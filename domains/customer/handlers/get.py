from typing import Optional

from flask import jsonify

from models import Guest


def get_customer(telephone: Optional[str]):
    if telephone:
        customers_with_equal_telephone = Guest.query.filter(Guest.telephone == telephone).all()
        customers_with_equal_telephone_ids = list(map(lambda x: x.id, customers_with_equal_telephone))

        customers_with_matched_telephone = Guest.query.filter(
            Guest.telephone.like(f"%{telephone}%") &
            Guest.id.notin_(customers_with_equal_telephone_ids)
        ).limit(
            100 - len(customers_with_equal_telephone)).all()

        all_customers = customers_with_equal_telephone + customers_with_matched_telephone

        return jsonify([Guest.to_json(customer) for customer in all_customers])

    return jsonify([Guest.to_json(customer) for customer in Guest.query.limit(100).all()])


def get_customer_comments(customer_id):
    customer = Guest.query.filter(Guest.id == customer_id).first()

    if customer is None:
        return {"msg": "Посетитель не найден"}, 400

    comments = [c.to_json(c) for c in customer.comments]
    comments.reverse()

    return jsonify(comments), 200
