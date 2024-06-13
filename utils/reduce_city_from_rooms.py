from functools import reduce


def reduce_city_from_rooms(rooms):
    return reduce(lambda acc, room: room.cinema.city or acc, rooms, None)
