import datetime


def parse_offset(tz: str) -> datetime.timezone:
    """'+07:00' -> timezone(+7ч)"""
    offset_hours, offset_minutes = map(int, tz.split(':'))
    return datetime.timezone(datetime.timedelta(hours=offset_hours, minutes=offset_minutes))


def set_tz(date: datetime.datetime, tz: str):
    return date.replace(tzinfo=parse_offset(tz))
