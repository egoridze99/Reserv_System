from datetime import datetime, timedelta
from typing import Optional

from constants.time import MOSCOW_OFFSET
from sqlite_functions.get_shift_date import get_shift_date


def compute_queue_dates(start_date: datetime, end_date: Optional[datetime], duration: float, timezone: Optional[str]):
    """Материализует служебные поля ReservationQueue, которые раньше пересчитывались
    на каждой строке в get_queue()/search_in_queue() (см. models/entities/buisness/ReservationQueue.py)."""

    timezone = timezone or MOSCOW_OFFSET

    duration_end_date = start_date + timedelta(hours=duration)
    window_end_date = (end_date or start_date) + timedelta(hours=duration)
    shift_date = get_shift_date(start_date, timezone, duration)

    return duration_end_date, window_end_date, shift_date
