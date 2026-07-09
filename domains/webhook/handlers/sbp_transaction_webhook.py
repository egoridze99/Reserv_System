from flask import request

from db import db
from models import Transaction, TransactionStatusEnum


def log(message: str):
    print(f"[sbp_transaction_webhook] {message}", flush=True)


def sbp_transaction_webhook():
    data = request.get_json(silent=True, force=True) or request.form.to_dict()

    log(f"incoming request: method={request.method} content_type={request.content_type} "
        f"headers={dict(request.headers)} raw_body={request.get_data(as_text=True)} parsed={data}")

    if "number" not in data or "status" not in data:
        log(f"skip: missing 'number' or 'status' in parsed data={data}")
        return "ok"

    number = str(data["number"])
    status = data["status"]

    log(f"number={number} status={status} type={data.get('type')}")

    if data.get("type") == "refund":
        log(f"skip: notification type is 'refund', number={number}")
        return "ok"

    transaction: "Transaction" = Transaction.query.filter_by(alias=number).first()

    if not transaction:
        log(f"skip: no transaction found with alias={number}")
        return "ok"

    log(f"found transaction id={transaction.id} current_status={transaction.transaction_status} "
        f"alias={transaction.alias}")

    if status == "success":
        transaction.transaction_status = TransactionStatusEnum.completed
    elif status == "fail":
        transaction.transaction_status = TransactionStatusEnum.rejected
    else:
        log(f"skip: unknown status={status} for transaction id={transaction.id}")
        return "skip update"

    db.session.add(transaction)
    db.session.commit()

    log(f"updated transaction id={transaction.id} to status={transaction.transaction_status}")
    return "ok", 200
