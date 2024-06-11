from datetime import datetime

from constants.time import MOSCOW_OFFSET
from utils.set_tz import set_tz


def is_date_in_last(date: datetime):
    now = set_tz(datetime.now(), MOSCOW_OFFSET)
    return now > date
