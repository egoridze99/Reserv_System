from typing import List

from datetime import datetime, timedelta, time

from domains.reservation.handlers.utils.check_the_taking import check_the_taking
from models import ReservationQueue, Reservation, QueueStatusEnum


def filter_expired_item(item: 'ReservationQueue', current_client_date: datetime):
    item_start_date = datetime.combine(item.date, item.start_time)
    item_end_date: datetime or None = None

    if item.end_time is not None:
        should_add_day = item.end_time < item.start_time
        date = item.date + timedelta(days=1) if should_add_day else item.date
        item_end_date = datetime.combine(date, item.end_time)

    return item_start_date >= current_client_date if item_end_date is None else item_end_date >= current_client_date


def search_available_items_from_queue(reservation: 'Reservation', current_client_date: datetime) -> List[
    'ReservationQueue']:
    reservation_start_date = datetime.combine(reservation.date, reservation.time)
    reservation_end_date = reservation_start_date + timedelta(hours=reservation.duration)

    queue_items: List[ReservationQueue] = ReservationQueue.query. \
        filter(ReservationQueue.date >= reservation_start_date.date()). \
        filter(ReservationQueue.date <= reservation_end_date.date()). \
        filter(ReservationQueue.status == QueueStatusEnum.active). \
        all()

    queue_items = list(filter(lambda i: filter_expired_item(i, current_client_date), queue_items))

    result = []
    for item in queue_items:
        if reservation.room not in item.rooms:
            continue

        item_start_time = item.start_time

        if item.end_time is None:
            is_free = False

            for room in item.rooms:
                is_free = is_free or not check_the_taking(item.date,
                                                          room,
                                                          item_start_time,
                                                          item.duration,
                                                          reservation.id)

            if is_free:
                result.append(item)
            continue

        step = datetime.combine(item.date, item_start_time)
        end_time_point = item.end_time
        end_date_point = item.date + timedelta(days=1) if end_time_point < time(12) else item.date
        end_point = datetime.combine(end_date_point, end_time_point)

        is_free = False
        while step <= end_point:
            for room in item.rooms:
                is_free = is_free or not check_the_taking(step.date(),
                                                          room,
                                                          step.time(),
                                                          item.duration,
                                                          reservation.id)

            if is_free:
                result.append(item)
                break

            step += timedelta(minutes=15)

    return result
