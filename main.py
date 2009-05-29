from Protocol import *
import pygame as pg
from pygame.locals import *

def main():
    pg.init()
    
    running = True
    p = Protocol("192.168.178.23", 1337, {})
    p.login("me", "foo", "bar")
    screen = pg.display.set_mode((800,600))
    
    while running:
        for event in pg.event.get():
            if event.type == QUIT:
                sys.exit()
        try:
            p.parse()
            screen.fill((0,0,0))
            pg.draw.circle(screen, (255,255,255), (20, 20), 10)
            pg.display.flip()
        except GTFOException as gtfo:
            print gtfo
            sys.exit()
        except socket.error as e:
            print "Socket Error: ", e
            sys.exit()
        except Exception as e:
            print e
            sys.exit()

if __name__ == "__main__":
    main()
