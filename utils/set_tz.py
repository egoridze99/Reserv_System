import datetime


def set_tz(date: datetime.datetime, tz: str):
    offset_hours, offset_minutes = map(int, tz.split(':'))
    offset = datetime.timedelta(hours=offset_hours, minutes=offset_minutes)
    tz = datetime.timezone(offset)

    return date.replace(tzinfo=tz)
