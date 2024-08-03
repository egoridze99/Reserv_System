from datetime import datetime

from models import TransactionStatusEnum, TransactionTypeEnum, Cinema, Transaction
from services.sbp_service import SbpService, SbpServiceException


def create_transaction(
        cinema: 'Cinema',
        transaction_type: str,
        amount: int,
        description: str,
        author_id: int
):
    transaction_status = TransactionStatusEnum.pending
    if TransactionTypeEnum[transaction_type] != TransactionTypeEnum.sbp:
        transaction_status = TransactionStatusEnum.completed

    transaction = Transaction(
        sum=amount,
        created_at=datetime.now(),
        description=description,
        cinema=cinema,
        author_id=author_id,
        transaction_type=TransactionTypeEnum[transaction_type],
        transaction_status=transaction_status,
    )

    if transaction.transaction_type == TransactionTypeEnum.sbp:
        sbp_transaction = SbpService.create_payment(transaction.id, transaction.sum, cinema.sbp_terminal_id)
        transaction.alias = sbp_transaction["id"]
        transaction.payment_url = sbp_transaction["payment_url"]

    return transaction
