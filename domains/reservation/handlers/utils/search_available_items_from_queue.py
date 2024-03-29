from typing import List

from datetime import datetime, timedelta, time

from sqlalchemy import func

from domains.reservation.handlers.utils.check_the_taking import check_the_taking
from models import ReservationQueue, Reservation, QueueStatusEnum


def filter_expired_item(item: 'ReservationQueue', current_client_date: datetime):
    return item.start_date >= current_client_date if item.end_date is None else item.end_date >= current_client_date


def search_available_items_from_queue(reservation: 'Reservation', current_client_date: datetime) -> List[
    'ReservationQueue']:
    reservation_end_date = reservation.date + timedelta(hours=reservation.duration)

    queue_items: List[ReservationQueue] = ReservationQueue.query. \
        filter(func.date(ReservationQueue.start_date) >= reservation.date.date()). \
        filter(func.date(ReservationQueue.start_date) <= reservation_end_date.date()). \
        filter(ReservationQueue.status == QueueStatusEnum.active). \
        all()

    queue_items = list(filter(lambda i: filter_expired_item(i, current_client_date), queue_items))

    result = []
    for item in queue_items:
        if reservation.room not in item.rooms:
            continue

        if item.end_date is None:
            is_free = False

            for room in item.rooms:
                is_free = is_free or not check_the_taking(item.start_date,
                                                          room,
                                                          item.duration,
                                                          reservation.id)

            if is_free:
                result.append(item)
            continue

        step = item.start_date
        end_point = item.end_date

        is_free = False
        while step <= end_point:
            for room in item.rooms:
                is_free = is_free or not check_the_taking(step,
                                                          room,
                                                          item.duration,
                                                          reservation.id)

            if is_free:
                result.append(item)
                break

            step += timedelta(minutes=15)

    return result
