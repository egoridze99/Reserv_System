from typing import List

from datetime import datetime, timedelta

from sqlalchemy import func

from constants.time import MOSCOW_OFFSET
from domains.reservation.handlers.utils.check_the_taking import check_the_taking
from models import ReservationQueue, Reservation, QueueStatusEnum
from utils.set_tz import set_tz


def search_available_items_from_queue(reservation: 'Reservation') -> List['ReservationQueue']:
    """Активные элементы очереди на зал резерва, которые можно посадить хотя бы в один из их залов"""
    reservation_end_date = reservation.date + timedelta(hours=reservation.duration)
    now = datetime.now()

    queue_items: List[ReservationQueue] = ReservationQueue.query. \
        filter(func.date(ReservationQueue.start_date) >= reservation.date.date()). \
        filter(func.date(ReservationQueue.start_date) <= reservation_end_date.date()). \
        filter(ReservationQueue.status == QueueStatusEnum.active). \
        all()

    return [item for item in queue_items
            if (item.end_date or item.start_date) >= now
            and reservation.room in item.rooms
            and any(not check_the_taking(set_tz(item.start_date, MOSCOW_OFFSET), room, item.duration, reservation.id)
                    for room in item.rooms)]
