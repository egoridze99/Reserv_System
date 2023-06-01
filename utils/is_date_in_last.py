from datetime import datetime


def is_date_in_last(date: datetime.date):
    now = datetime.now().date()
    return now > date
