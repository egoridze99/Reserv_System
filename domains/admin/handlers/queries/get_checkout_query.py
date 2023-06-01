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