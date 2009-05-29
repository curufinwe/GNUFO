import pygame as pg
from pygame.locals import *

from Protocol import *
from Renderer import Renderer

def main():
    pg.init()
    
    running = True
    gamestatus = {}
    p = Protocol("192.168.178.23", 1337, gamestatus)
    p.login("me", "foo", "bar")
    screen = pg.display.set_mode((800,600))
    clock = pg.time.Clock()
    renderer = Renderer(gamestatus, screen)
    
    while running:
        time = clock.tick(100)
        if time > 11:
            print time
        for event in pg.event.get():
            if event.type == QUIT:
                sys.exit()
        try:
            p.parse()
            renderer.render()
            pg.display.flip()
        except GTFOException as gtfo:
            print gtfo
            sys.exit()
        except socket.error as e:
            print "Socket Error: ", e
            sys.exit()
        #except Exception as e:
        #    print e
        #   sys.exit()

if __name__ == "__main__":
    main()
