import logging

from core.enums.map_enums import MapsEnum
from core.exceptions.map_not_existent_exception import MapNotExistentException
from core.game_world import GameWorld
from core.manager.asset_manager import AssetManager
from core.map.map import Map
from core.map.maps.main_world import MainWorldMap
from core.settings.maps_assets import NATURE_PROPS
from core.singleton_meta import SingletonMeta


class MapManager(metaclass=SingletonMeta):
    _current_map: Map | None = None
    _current_map_enum: MapsEnum | None = None
    _maps: dict[MapsEnum, Map]

    _logger = logging.getLogger("MapManager")

    def __init__(self):
        self._logger.info("Initializing MapManager...")
        self._maps = {}
        self._load_props()

        self._maps = {MapsEnum.MAIN_WORLD: MainWorldMap()}

        self._logger.info("MapManager initialized successfully.")

    def _is_map_valid(self, map_enum: MapsEnum) -> bool:
        if map_enum not in self._maps:
            self._logger.error(f"Map not found: {map_enum.value}")
            raise MapNotExistentException(map_enum.value)
        return True

    def get_map(self, map_enum: MapsEnum) -> Map:
        self._logger.info(f"Getting map: {map_enum.value}")
        if not self._is_map_valid(map_enum):
            raise MapNotExistentException(map_enum.value)
        return self._maps[map_enum]

    def change_map(self, map_enum: MapsEnum, world: GameWorld):
        self._logger.info(f"Changing map to: {map_enum.value}")
        if not self._is_map_valid(map_enum):
            return

        map = self._maps[map_enum]
        map.instantiate(world)

        self._current_map = map
        self._current_map_enum = map_enum

    def _load_props(self):
        self._logger.info("Loading props...")
        self._load_nature_props()
        self._logger.info("Props loaded successfully.")

    def _load_nature_props(self):
        self._logger.info("Loading nature props...")

        for file in NATURE_PROPS.glob("*.png"):
            name = file.stem
            AssetManager().load_image(name, str(file))

        self._logger.info("Nature props loaded successfully.")
