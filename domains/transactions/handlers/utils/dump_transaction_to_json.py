from models import Transaction


def dump_transaction_to_json(transaction: 'Transaction'):
    data = Transaction.to_json(transaction)
    del data["author"]

    return data
