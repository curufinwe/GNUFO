import pygame as pg
from pygame.locals import *

SIZES = [1, 3, 10, 15]

class Renderer():
    def __init__(self, gamestatus, screen):
        self._gamestatus = gamestatus
        self._screen = screen
        self.background_color = (0, 0, 0)
        self.sprites = {1: {}, 2:{}, 3:{}}

    def render(self):
        self._screen.fill(self.background_color)
        for obj in self._gamestatus["objects"].itervalues():
            gfx = obj["gfx"]
            if gfx >= 1 and gfx <= 3:
                id = _colorToInt(obj["color"])
                if id not in self.sprites[gfx]:
                    self.sprites[gfx][id] = _createSprite(SIZES[gfx],
                                                          obj["color"])
                self._screen.blit(self.sprites[gfx][id],
                     (obj["pos"][0] - SIZES[gfx], obj["pos"][1] - SIZES[gfx]))
                

def _colorToInt(color):
    return color[0] + color[1] * 256 + color[2] * 65536

def _createSprite(radius, color):
    sprite = pg.Surface((radius*2,radius*2), HWSURFACE | SRCALPHA)
    pg.draw.circle(sprite, color, (radius, radius), radius)
    return sprite
