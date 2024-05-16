def get_duration_query(area, until, till):
    return f"""select
       {area}.name as area,
       sum(reservation.duration) as sum
from reservation
    join room on reservation.room_id = room.id
    join cinema on room.cinema_id = cinema.id
where
    reservation.date between '{until}' and '{till}' and
    reservation.status = 'finished'
group by {area}.id;
"""
