from datetime import datetime, time, timedelta
from typing import Optional

from constants.time import MOSCOW_OFFSET
from sqlite_functions.get_shift_date import get_shift_date
from utils.convert_tz import convert_tz


def compute_queue_dates(data: dict, timezone: Optional[str]) -> Optional[dict]:
    """Переводит дату и время из запроса в поля дат ReservationQueue, включая служебные
    (см. models/entities/buisness/ReservationQueue.py). None, если временной диапазон неверный."""

    timezone = timezone or MOSCOW_OFFSET
    duration = data['duration']

    date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    start_time = datetime.strptime(data['start_time'], '%H:%M').time()
    start_date = convert_tz(datetime.combine(date, start_time), timezone, True)
    end_date = None

    if data['end_time']:
        end_time = datetime.strptime(data['end_time'], '%H:%M').time()

        if start_time > end_time > time(8):
            return None

        end_day = date + timedelta(days=1) if end_time < start_time else date
        end_date = convert_tz(datetime.combine(end_day, end_time), timezone, True)

    return {
        "start_date": start_date,
        "end_date": end_date,
        "duration_end_date": start_date + timedelta(hours=duration),
        "window_end_date": (end_date or start_date) + timedelta(hours=duration),
        "shift_date": get_shift_date(start_date, timezone, duration),
    }
