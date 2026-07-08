import os
from pathlib import Path

import pygame

from utils.resource_path import resource_path

def load_image(image_path: os.PathLike | str, size: tuple[int, int] | None = None, scale: float | None = None) -> pygame.Surface:
    caminho_imagem = resource_path(str(image_path))

    if type(caminho_imagem) is str:
        caminho_imagem = Path(caminho_imagem)

    if type(caminho_imagem) is Path and not caminho_imagem.is_file():
        raise FileNotFoundError(f"Image file '{caminho_imagem}' not found.")
    
    image = pygame.image.load(caminho_imagem).convert_alpha()
    if size is not None:
        image = pygame.transform.scale(image, size)
    if scale is not None:
        image = pygame.transform.scale(image, (int(image.get_width() * scale), int(image.get_height() * scale)))
    return image