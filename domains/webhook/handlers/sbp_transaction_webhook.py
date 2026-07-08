from flask import request

from db import db
from models import Transaction, TransactionStatusEnum


def sbp_transaction_webhook():
    data = request.get_json(silent=True, force=True) or request.form.to_dict()
    number = str(data["number"])
    status = data["status"]

    if data["type"] == "refund":
        return "ok"

    transaction: "Transaction" = Transaction.query.filter_by(alias=number).first()

    if status == "success":
        transaction.transaction_status = TransactionStatusEnum.completed
    elif status == "fail":
        transaction.transaction_status = TransactionStatusEnum.rejected
    else:
        return "skip update"

    db.session.add(transaction)
    db.session.commit()
    return "ok", 200
