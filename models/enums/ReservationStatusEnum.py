import enum


class ReservationStatusEnum(enum.Enum):
    not_allowed = "not_allowed"
    progress = 'progress'
    waiting = 'waiting'
    finished = 'finished'
    canceled = 'canceled'