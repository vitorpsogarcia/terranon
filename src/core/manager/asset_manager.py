from typing import ClassVar, TypedDict

import pygame

from core.exceptions.asset_not_found_exception import AssetNotFoundException
from core.settings.settings import ASSETS_FOLDER
from core.singleton_meta import SingletonMeta
from utils.image import load_image


class AssetsDict(TypedDict):
    images: dict[str, pygame.Surface]
    fonts: dict[str, pygame.font.Font]
    sounds: dict[str, pygame.mixer.Sound]


class AssetManager(metaclass=SingletonMeta):
    def __init__(self):
        self._assets: AssetsDict = {"images": {}, "fonts": {}, "sounds": {}}
        self._sound_cache: dict[str, pygame.mixer.Sound] = {}

    def load_image(
        self,
        name: str,
        path: str,
        size: tuple[int, int] | None = None,
        scale: float | None = None,
        **kwargs,
    ):
        if name not in self._assets["images"]:
            try:
                image = load_image(
                    ASSETS_FOLDER / "images" / path, size=size, scale=scale, **kwargs
                )
                self._assets["images"][name] = image
                return image
            except (pygame.error, FileNotFoundError):
                raise AssetNotFoundException(name)
        return self._assets["images"].get(name)

    def get_image(self, name: str) -> pygame.Surface:
        asset = self._assets["images"].get(name)
        if asset is None:
            raise AssetNotFoundException(name, message="Image not loaded")

        return asset

    def load_font(self, name: str, path: str, size: int):
        key = f"{name}_{size}"
        if key not in self._assets["fonts"]:
            try:
                font = pygame.font.Font(ASSETS_FOLDER / "fonts" / path, size)
                self._assets["fonts"][key] = font
            except pygame.error:
                raise AssetNotFoundException(name)
        return self._assets["fonts"].get(key)

    def get_font(self, name: str, size: int) -> pygame.font.Font:
        font = self._assets["fonts"].get(f"{name}_{size}")
        if font is None:
            raise AssetNotFoundException(name, message="Font not loaded")
        return font

    def get_sound(self, path: str) -> pygame.mixer.Sound:
        if path not in self._sound_cache:
            try:
                sound = pygame.mixer.Sound(ASSETS_FOLDER / "sounds" / path)
                self._sound_cache[path] = sound
            except (pygame.error, FileNotFoundError):
                raise AssetNotFoundException(path)

        sound = self._sound_cache.get(path)
        if sound is None:
            raise AssetNotFoundException(path, message="Sound not loaded")

        return sound
