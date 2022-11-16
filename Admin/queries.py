def get_money_query(area, until, till):
    return f"""select
       {area}.name as area,
       sum(reservation.cash) as cash,
       sum(reservation.card) as card,
       sum(reservation.sum_rent) as sum
from reservation
    join room on reservation.room_id = room.id
    join cinema on room.cinema_id = cinema.id
where
    reservation.date >= '{until}' and
    reservation.date <= '{till}' and
    reservation.status = 'finished'
group by {area}.id;
"""


def get_checkout_query(area, until, till):
    return f"""
        select
        {area}_name as area,
        sum(sum) as sum
    from (
        select
            reservation.id as reservation_id,
            room.id as room_id,
            room.name as room_name,
            cinema.id as cinema_id,
            cinema.name as cinema_name,
            sum(checkout.sum) as sum
        from reservation
            join room on room.id = reservation.room_id
            join cinema on cinema.id = room.cinema_id
            join checkout_reservation cr on reservation.id = cr.reservation_id
            join checkout on checkout.id = cr.checkout_id
        where
            reservation.date >= '{until}' and
            reservation.date <= '{till}' and
            reservation.status = 'finished'
        group by cr.reservation_id)
    group by {area}_name;
"""


def get_duration_query(area, until, till):
    return f"""select
       {area}.name as area,
       sum(reservation.duration) as sum
from reservation
    join room on reservation.room_id = room.id
    join cinema on room.cinema_id = cinema.id
where
    reservation.date >= '{until}' and
    reservation.date <= '{till}' and
    reservation.status = 'finished'
group by {area}.id;
"""
