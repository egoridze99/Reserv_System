from datetime import datetime


def parse_date(date: str) -> datetime.date:
    return datetime.strptime(date, '%Y-%m-%d').date()
