from datetime import date as date_cls, datetime, time, timedelta

from utils.convert_tz import convert_tz


def get_shift_date(start_date: datetime, timezone: str, duration: float) -> date_cls:
    """Возвращает дату "смены" (рабочего дня), к которой относится начало брони.

    Смена длится с 8:00 до 8:00 следующего дня, поэтому бронь, начинающаяся
    и заканчивающаяся до 8:00, всё ещё относится к предыдущей смене.
    """
    local_date = convert_tz(start_date, timezone, False)
    finish_date = local_date + timedelta(hours=duration)

    if finish_date.time() < time(8) and local_date.date() == finish_date.date():
        return (local_date - timedelta(days=1)).date()

    return local_date.date()
