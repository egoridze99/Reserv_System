import json
from typing import List

from models import Reservation, Checkout


def dump_reservation_to_update_log(reservation: 'Reservation'):
    return json.dumps({
        "date": reservation.date.strftime("%d-%m-%Y %H:%M"),
        "room": reservation.room.name,
        "duration": reservation.duration,
        "count": reservation.count,
        "film": reservation.film,
        "note": reservation.note,
        "status": reservation.status.name,
        "sum_rent": reservation.sum_rent,
        "card": reservation.card,
        "cash": reservation.cash,
        "guest_name": reservation.guest.name,
        "guest_telephone": reservation.guest.telephone,
        "certificate_ident": reservation.certificate.ident if reservation.certificate else None,
        "checkouts": [{"description": item.description, "sum": item.sum} for item in reservation.checkout]
    })