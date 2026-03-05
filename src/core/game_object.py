from pygame import Vector2
from pygame.sprite import Sprite
from pygame.rect import Rect

from utils.image import load_image

class GameObject(Sprite):
    def __init__(self, pos: Vector2, image: str | None = None , size_x: int | None = None, size_y: int | None = None):
        super().__init__()
        self._pos = pos
        self._size_x = size_x
        self._size_y = size_y
        
        if image is not None:
            self._image = load_image(image, size_x, size_y)
        elif size_x is not None and size_y is not None:
            self._image = Rect(0, 0, size_x, size_y)
        else:
            raise ValueError("Either an image path or both size_x and size_y must be provided.")
    
    