from datetime import datetime

from constants.time import MOSCOW_OFFSET
from utils.set_tz import parse_offset


def convert_tz(date: 'datetime', tz: str, to_moscow: bool = False) -> datetime:
    tz, moscow_tz = parse_offset(tz), parse_offset(MOSCOW_OFFSET)

    if to_moscow:
        return date.replace(tzinfo=tz).astimezone(moscow_tz)

    return date.replace(tzinfo=moscow_tz).astimezone(tz)
