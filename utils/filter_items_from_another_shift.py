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

    has_time_attribute = isinstance(item, Reservation)

    # Дата окончания резерва
    item_end_date = datetime.combine(item.date, item.time if has_time_attribute else item.end_time) \
                    + timedelta(hours=item.duration)
    if item_end_date.date() not in [date, date + timedelta(days=1)]:
        return False

    if item_end_date.time() <= time(8):
        if item.date != date:
            return True

        return item.date != item_end_date.date()

    return item.date == date
