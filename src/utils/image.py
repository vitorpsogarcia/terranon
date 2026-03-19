from os import path
from pathlib import Path

import pygame

def load_image(image_path: Path, size_x: int | None = None, size_y: int | None = None) -> pygame.Surface:

    if not image_path.is_file():
        raise FileNotFoundError(f"Image file '{image_path}' not found.")
    
    image = pygame.image.load(image_path).convert_alpha()
    if size_x is not None and size_y is not None:
        image = pygame.transform.scale(image, (size_x, size_y))
    return image