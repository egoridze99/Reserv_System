from typing import Optional, List

from flask import jsonify

from models import Guest, GuestChangesLogs


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


def get_customer_by_id(ids: List[int]):
    customers = Guest.query.filter(Guest.id.in_(ids)).all()

    return jsonify([Guest.to_json(customer) for customer in customers])


def get_customer_comments(customer_id):
    customer = Guest.query.filter(Guest.id == customer_id).first()

    if customer is None:
        return {"msg": "Посетитель не найден"}, 400

    comments = [c.to_json(c) for c in customer.comments]
    comments.reverse()

    return jsonify(comments), 200


def get_logs(customer_id: int):
    logs = GuestChangesLogs.query.filter(GuestChangesLogs.guest_id == customer_id).all()
    logs = [GuestChangesLogs.to_json(log) for log in logs]
    logs.sort(key=lambda x: x['created_at'])

    return jsonify(logs)
