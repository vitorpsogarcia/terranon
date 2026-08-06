from typing import ClassVar, TypedDict

import pygame

from core.exceptions.asset_not_found_exception import AssetNotFoundException
from core.settings.settings import ASSETS_FOLDER
from utils.image import load_image


class AssetsDict(TypedDict):
    images: dict[str, pygame.Surface]
    fonts: dict[str, pygame.font.Font]
    sounds: dict[str, pygame.mixer.Sound]


class AssetManager:
    _instance = None
    _assets: ClassVar[AssetsDict] = {"images": {}, "fonts": {}, "sounds": {}}
    _sound_cache: ClassVar[dict[str, pygame.mixer.Sound]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def load_image(
        cls,
        name: str,
        path: str,
        size: tuple[int, int] | None = None,
        scale: float | None = None,
        **kwargs,
    ):
        if name not in cls._assets["images"]:
            try:
                image = load_image(
                    ASSETS_FOLDER / "images" / path, size=size, scale=scale, **kwargs
                )
                cls._assets["images"][name] = image
                return image
            except (pygame.error, FileNotFoundError):
                raise AssetNotFoundException(name)
        return cls._assets["images"].get(name)

    @classmethod
    def get_image(cls, name: str) -> pygame.Surface:
        asset = cls._assets["images"].get(name)
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

    @classmethod
    def get_sound(cls, path: str) -> pygame.mixer.Sound:
        if path not in cls._sound_cache:
            try:
                sound = pygame.mixer.Sound(ASSETS_FOLDER / "sounds" / path)
                cls._sound_cache[path] = sound
            except (pygame.error, FileNotFoundError):
                raise AssetNotFoundException(path)

        sound = cls._sound_cache.get(path)
        if sound is None:
            raise AssetNotFoundException(path, message="Sound not loaded")

        return sound
