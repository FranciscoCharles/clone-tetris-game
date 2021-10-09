from os import environ
if 'PYGAME_HIDE_SUPPORT_PROMPT' not in environ:
    environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hidden'
del environ

from PIL import Image
from pygame import Surface
from typing import Tuple, Optional
import pygame


def image_pill2pygame(image) -> Surface:
    data = image.tobytes()
    size = image.size
    mode = image.mode
    return pygame.image.fromstring(data, size, mode)

def image_pygame2pill(image, mode='RGBA') -> Image.Image:
    data = pygame.image.tostring(image, mode)
    size = image.get_size()
    return Image.frombytes(mode, size, data)

def pill_img_open_and_resize(filename: str, size: Optional[Tuple[int, int]] = (60, 60)) -> Surface:
    image = Image.open(filename)
    image = image.resize(size, Image.ANTIALIAS)
    return image_pill2pygame(image)

def pygame_img_resize(image, size: Optional[Tuple[int, int]] = (60, 60), mode='RGBA') -> Surface:
    image = image_pygame2pill(image, mode)
    image = image.resize(size, Image.ANTIALIAS)
    return image_pill2pygame(image)