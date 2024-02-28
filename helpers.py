import os
import pygame
import math

def relative_to_file(relpath: str) -> str:
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        relpath
    )

def load_image(relpath: str):
    return pygame.image.load(relative_to_file(relpath))

def rotateSurf(surf: pygame.Surface, orientation: tuple[int,int],addition:int=0) -> pygame.Surface:
    return pygame.transform.rotate(
        surf,
        math.degrees(math.atan2(-orientation[1],orientation[0]))+addition
    )