import json

from models import Reservation, Guest


def dump_reservation_to_update_log(reservation: 'Reservation', guest: 'Guest'):
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
        "guest_name": guest.name,
        "guest_telephone": guest.telephone,
        "certificate_ident": reservation.certificate.ident if reservation.certificate else None,
    })
