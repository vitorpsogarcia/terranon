from enum import Enum


class MapLayersEnum(Enum):
    ENEMY_ROUTES = 'enemy_routes'
    WAYPOINTS = 'waypoints'
    GROUND = 'ground'
    SPAWNERS = 'spawners'
    TREES = 'trees'
    COLLISION = 'collision'