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