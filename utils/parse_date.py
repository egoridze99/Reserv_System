from datetime import datetime, time, timedelta


def parse_date(date: str) -> datetime.date:
    return datetime.strptime(date, '%Y-%m-%d').date()


def parse_shift_range(since: str, till: str):
    """Границы периода по сменам: с 8:00 первого дня до 8:00 дня, следующего за последним"""
    return datetime.combine(parse_date(since), time(8)), datetime.combine(parse_date(till) + timedelta(days=1), time(8))
