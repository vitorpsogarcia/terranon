from enum import Enum

class ProjectileVariantEnum(Enum):
    DEFAULT = ("default", 4)

    def __init__(self, variant_name: str, frames: int):
        self.variant_name = variant_name
        self.frames = frames
