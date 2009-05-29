import pygame as pg

SIZES = [1, 3, 10, 15]

class Renderer():
    def __init__(self, gamestatus, screen):
        self._gamestatus = gamestatus
        self._screen = screen
        self.background_color = (0, 0, 0)

    def render(self):
        self._screen.fill(self.background_color)
        for obj in self._gamestatus["objects"].itervalues():
            if obj["gfx"] >= 1 and obj["gfx"] <= 3:
                pg.draw.circle(self._screen, obj["color"], obj["pos"],
                               SIZES[obj["gfx"]])