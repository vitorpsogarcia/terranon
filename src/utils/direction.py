from pygame import Vector2


def get_direction_str_by_vector(vector: Vector2) -> str:
    if vector.x == 0 and vector.y < 0:
        return "N"
    elif vector.x == 0 and vector.y > 0:
        return "S"
    elif vector.x < 0 and vector.y == 0:
        return "W"
    elif vector.x > 0 and vector.y == 0:
        return "E"
    elif vector.x < 0 and vector.y < 0:
        return "NW"
    elif vector.x > 0 and vector.y < 0:
        return "NE"
    elif vector.x < 0 and vector.y > 0:
        return "SW"
    elif vector.x > 0 and vector.y > 0:
        return "SE"
    else:
        return "S"