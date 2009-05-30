from socket import error
import pygame as pg
from pygame.locals import *

from Protocol import *
from Renderer import Renderer

def main():
    pg.init()
    pg.event.set_grab(True)
    pg.mouse.set_visible(False)
    
    running = True
    gamestatus = {}
    try:
        p = Protocol("127.0.0.1", 1337, gamestatus)
        p.login("me", "foo", "bar")
    except socket.error as e:
        if e.errno == 111: #Connection refused
            print "Connection could not be established"
            sys.exit()
        else:
            print e
    screen = pg.display.set_mode((800,600))
    clock = pg.time.Clock()
    renderer = Renderer(gamestatus, screen)
    rel_mv = [0.0, 0.0]
    lst_mv = [0.0, 0.0]
    diff = [0.0, 0.0]
    max_diff = [0.1, 0.1]

    keytable = {K_j: 0x1, K_k: 0x2}
    keystatustable = {KEYDOWN: 0x1, KEYUP: 0x0}

    total = 0
    count = 0
    while running:
        time = clock.tick(60)
        if time == 0:
            time = 1
        total += time
        count += 1
        for event in pg.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN or event.type == KEYUP:
                print event.key
                if event.key == K_ESCAPE:
                    running = False
                if event.key in keytable:
                    p.sendKeyStatus(keytable[event.key],
                                    keystatustable[event.type])
        abs_mv = pg.mouse.get_rel()
        rel_mv = [abs_mv[0]/float(time), abs_mv[1]/float(time)]

        if rel_mv[0] > lst_mv[0]:
            diff[0] = rel_mv[0] - lst_mv[0]
        else:
            diff[0] = lst_mv[0] - rel_mv[0]
        if rel_mv[1] > lst_mv[1]:
            diff[1] = rel_mv[1] - lst_mv[1]
        else:
            diff[1] = lst_mv[1] - rel_mv[1]
        
        if diff[0] > max_diff[0] or diff[1] > max_diff[1]:
            print rel_mv
            p.sendMouse(velocity=rel_mv)

        lst_mv = rel_mv
        
        try:
            p.update(time)
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
    print 1000.0 / (total / float(count))

if __name__ == "__main__":
    main()
