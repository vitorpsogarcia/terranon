import os
from pathlib import Path

import pygame

def load_image(image_path: os.PathLike | str, size: tuple[int, int] | None = None, scale: float | None = None) -> pygame.Surface:

    if type(image_path) is str:
        image_path = Path(image_path)

    if type(image_path) is Path and not image_path.is_file():
        raise FileNotFoundError(f"Image file '{image_path}' not found.")
    
    image = pygame.image.load(os.fspath(image_path)).convert_alpha()
    if size is not None:
        image = pygame.transform.scale(image, size)
    if scale is not None:
        image = pygame.transform.scale(image, (int(image.get_width() * scale), int(image.get_height() * scale)))
    return image