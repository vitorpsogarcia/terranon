from os import path

import pygame

def load_image(relative_path: str, size_x: int | None = None, size_y: int | None = None) -> pygame.Surface:

    full_path = path.join(path.dirname(__file__), relative_path)

    if not path.isfile(full_path):
        raise FileNotFoundError(f"Image file '{full_path}' not found.")
    
    image = pygame.image.load(full_path).convert_alpha()
    if size_x is not None and size_y is not None:
        image = pygame.transform.scale(image, (size_x, size_y))
    return image