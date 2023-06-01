import enum


class QueueStatusEnum(enum.Enum):
    active = "active"
    expired = 'expired'
    reserved = 'reserved'
    canceled = 'canceled'
    waiting = 'waiting'
