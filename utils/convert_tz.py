from datetime import datetime, timedelta, timezone

from constants.time import MOSCOW_OFFSET


def convert_tz(date: 'datetime', tz: str, to_moscow: bool) -> datetime:
    offset_hours, offset_minutes = map(int, tz.split(':'))
    offset = timedelta(hours=offset_hours, minutes=offset_minutes)
    tz = timezone(offset)

    moscow_offset_hours, moscow_offset_minutes = map(int, MOSCOW_OFFSET.split(':'))
    moscow_offset = timedelta(hours=moscow_offset_hours, minutes=moscow_offset_minutes)
    moscow_tz = timezone(moscow_offset)

    if to_moscow:
        date_with_timezone = date.replace(tzinfo=tz)
        return date_with_timezone.astimezone(moscow_tz)
    else:
        date_with_timezone = date.replace(tzinfo=moscow_tz)
        return date_with_timezone.astimezone(tz)
