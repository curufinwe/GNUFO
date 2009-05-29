from Protocol import *
from PySFML import sf

def main():
    #p = Protocol("192.168.178.43", 1337, {})
    #p.login("me", "foo", "bar")
    app = sf.RenderWindow(sf.VideoMode(800, 600, 32), "GNUFO",
                          sf.Style.Close | sf.Style.Resize,
                          sf.WindowSettings(24,8,0))
    evtHandler = sf.Event()
    while app.IsOpened():
        while app.GetEvent(evtHandler):
            if evtHandler.Type == sf.Event.Closed:
                app.Close()
            if evtHandler.Type == sf.Event.KeyPressed and \
               evtHandler.Key.Code == sf.Key.Escape:
                app.Close()
        try:
            #p.parse()
            app.Clear(sf.Color.Black)
            app.Display()
        except GTFOException as gtfo:
            print gtfo
            sys.exit()
        except Exception as e:
            print e
            sys.exit()

if __name__ == "__main__":
    main()
