import logging

from core.asset_manager import AssetManager
from core.enums.map_enums import MapsEnum
from core.exceptions.map_not_existent_exception import MapNotExistentException
from core.game_world import GameWorld
from core.map.map import Map
from core.map.maps.main_world import MainWorldMap
from core.settings.maps_assets import NATURE_PROPS


class MapManager:
    _instance = None
    _current_map: Map | None = None
    _current_map_enum: MapsEnum | None = None
    _maps: dict[MapsEnum, Map]

    _logger = logging.getLogger("MapManager")

    def __init__(self):
        raise RuntimeError("MapManager is a static class and cannot be instantiated.")

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._maps = {}
        return cls._instance

    @classmethod
    def _is_map_valid(cls, map_enum: MapsEnum) -> bool:
        if map_enum not in cls._maps:
            cls._logger.error(f"Map not found: {map_enum.value}")
            raise MapNotExistentException(map_enum.value)
        return True

    @classmethod
    def initialize(cls):
        cls._logger.info("Initializing MapManager...")

        if cls._instance is not None:
            raise RuntimeError("MapManager has already been initialized.")

        cls._load_props()

        cls._maps = {MapsEnum.MAIN_WORLD: MainWorldMap()}

        cls._logger.info("MapManager initialized successfully.")

    @classmethod
    def get_map(cls, map_enum: MapsEnum) -> Map | None:
        cls._logger.info(f"Getting map: {map_enum.value}")
        if not cls._is_map_valid(map_enum):
            return
        return cls._maps[map_enum]

    @classmethod
    def change_map(cls, map_enum: MapsEnum, world: GameWorld):
        cls._logger.info(f"Changing map to: {map_enum.value}")
        if not cls._is_map_valid(map_enum):
            return

        map = cls._maps[map_enum]
        map.instantiate(world)

        cls._current_map = map
        cls._current_map_enum = map_enum

    @classmethod
    def _load_props(cls):
        cls._logger.info("Loading props...")
        cls._load_nature_props()
        cls._logger.info("Props loaded successfully.")

    @classmethod
    def _load_nature_props(cls):
        cls._logger.info("Loading nature props...")

        for file in NATURE_PROPS.glob("*.png"):
            name = file.stem
            AssetManager.load_image(name, str(file))

        cls._logger.info("Nature props loaded successfully.")
