from flask import request

from db import db
from models import Transaction, TransactionStatusEnum
from utils.parse_json import parse_json


def sbp_transaction_webhook():
    data = parse_json(request.data)
    transaction_id = data["order"]["id"]
    status = data["status"]

    transaction: "Transaction" = Transaction.query.filter_by(id=transaction_id).first()

    if status == "successful":
        transaction.transaction_status = TransactionStatusEnum.completed
    elif status == "error":
        transaction.transaction_status = TransactionStatusEnum.rejected
    else:
        return "skip update"

    db.session.add(transaction)
    db.session.commit()
    return "ok", 200
