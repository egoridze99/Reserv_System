from enum import Enum


class TransactionStatusEnum(Enum):
    pending = "pending"
    rejected = "rejected"
    completed = "completed"
    refunded = "refunded"
