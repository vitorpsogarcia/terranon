class MapNotExistentException(Exception):
    
    def __init__(self, map_name: str, message: str = "Map not existent"):
        self.map_name = map_name
        self.message = f"{message}: {map_name}"
        super().__init__(self.message)