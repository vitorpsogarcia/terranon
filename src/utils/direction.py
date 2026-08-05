from pygame import Vector2


from pygame.math import Vector2

def get_direction_str_by_vector(vector: Vector2) -> str | None:
    if vector.length() == 0:
        return None
 
    if abs(vector.x) > abs(vector.y):
        if vector.x > 0:
            return "E" 
        else:
            return "W"  
    else:
        if vector.y > 0:
            return "S" 
        else:
            return "N" 