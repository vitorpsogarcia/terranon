import pygame

from core.exceptions.asset_not_found_exception import AssetNotFoundException
from utils.image import load_image

from core.settings.settings import ASSETS_FOLDER

class AssetManager:
    _instance = None
    _assets = {
        "images": {},
        "fonts": {},
        "sounds": {}
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AssetManager, cls).__new__(cls)
        return cls._instance

    @classmethod
    def load_image(cls, name: str, path: str, **kwargs):
        if name not in cls._assets["images"]:
            try:
                image = load_image(ASSETS_FOLDER / "images" / path, **kwargs)
                cls._assets["images"][name] = image
            except pygame.error:
                raise AssetNotFoundException(name)
        return cls._assets["images"].get(name)

    @classmethod
    def get_image(cls, name: str) -> pygame.Surface:
        asset =  cls._assets["images"].get(name)
        if asset is None:
            raise AssetNotFoundException(name, message="Image not loaded")
    
        return asset

    @classmethod
    def load_font(cls, name: str, path: str, size: int):
        key = f"{name}_{size}"
        if key not in cls._assets["fonts"]:
            try:
                font = pygame.font.Font(ASSETS_FOLDER / "fonts" / path, size)
                cls._assets["fonts"][key] = font
            except pygame.error:
                raise AssetNotFoundException(name)
        return cls._assets["fonts"].get(key)

    @classmethod
    def get_font(cls, name: str, size: int) -> pygame.font.Font:
        font = cls._assets["fonts"].get(f"{name}_{size}")
        if font is None:
            raise AssetNotFoundException(name, message="Font not loaded")
        return font
