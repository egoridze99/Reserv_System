from abc import ABC
from datetime import datetime, timedelta, time

from models import Reservation, ReservationQueue


class AbstractItemWithDate(ABC):
    date: datetime.date
    time: datetime.time
    end_time: datetime.time
    duration: int


def filter_items_from_another_shift(item: 'Reservation' or 'ReservationQueue', date: datetime.date):
    """
    Приложение должно мыслить сменами. Если резерв заканчивается до 8 утра, то
    он должен выводиться вместе с резервами за предыдущий день.

    Данный фильтр показывает, должен ли резерв выводиться вместе с резервами за выбранную дату
    """

    if isinstance(item, ReservationQueue):
        if item.end_time is None:
            shift_date = item.date
            time_point = item.start_time
        else:
            shift_date = item.date if item.end_time > item.start_time else item.date + timedelta(days=1)
            time_point = item.end_time
    else:
        shift_date = item.date
        time_point = item.time

    # Дата окончания резерва
    item_end_date = datetime.combine(shift_date, time_point) \
                    + timedelta(hours=item.duration)

    if item_end_date.date() not in [date, date + timedelta(days=1)]:
        return False

    if item_end_date.time() <= time(8):
        if shift_date != date:
            return True

        return shift_date != item_end_date.date()

    return shift_date == date
