import json

from models import Transaction, TransactionStatusEnum, TransactionChangesLog, TransactionTypeEnum
from services.sbp_service import SbpService
from utils.transactions.dump_transaction_to_json import dump_transaction_to_json


def make_refund(transaction: 'Transaction', author_name: str):
    if transaction.transaction_status == TransactionStatusEnum.refunded:
        return transaction, None

    old_values = json.dumps(dump_transaction_to_json(transaction))
    transaction.transaction_status = TransactionStatusEnum.refunded
    new_values = json.dumps(dump_transaction_to_json(transaction))

    log = TransactionChangesLog(transaction_id=transaction.id,
                                author=author_name, new=new_values, old=old_values)

    if transaction.transaction_type == TransactionTypeEnum.sbp:
        SbpService.make_refund(transaction.alias, transaction.sum)

    return transaction, log
