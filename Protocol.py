import socket
import sys
import struct

import connection

class Protocol(object):

    def __init__(self, serverip, port, gamestatus):
        try:
            connection.connect(serverip, port)
        except socket.error as e:
            #print e
            if e.errno == 115:
                #This error means that everything is alright
                #(Operation now in Progress)
                self.__setup(gamestatus)
            else:
                sys.exit()
        else:
            self.__setup(gamestatus)

    def __setup(self, gamestatus):
        if not hasattr(gamestatus, "objects"):
            gamestatus["objects"] = dict()
        self.gamestatus = gamestatus
        connection.magic_number = '\x21'
        connection.rules = {
            '\x23' : {'name': 'update',
                      'processor': ['=HffffBBBB', 'id', 'velx', 'vely', 'posx',
                                    'posy', 'gfx', 'colR', 'colG', 'colB']
                     },
            '\x24' : {'name': 'updatePos',
                      'processor': ['=Hffff', 'id', 'velx', 'vely', 'posx',
                                    'posy']
                     },
            '\x25' : {'name': 'updateGfx',
                      'processor': ['=HBBBB', 'id', 'gfx', 'colR', 'colG',
                                    'colB']
                     },
            '\x26' : {'name': 'delete', 'processor' : ['H', 'id']},
            '\x27' : {'name': 'loginAck', 'processor': ['B', 'status']},
            '\x28' : {'name': 'status', 'processor': status},
            '\x29' : {'name': 'message', 'processor': message},
            '\x2A' : {'name': 'GTFO', 'processor': ['']}
        }
            

    def login(self, user, serverpw, userpw):
        packet = struct.pack("=B16s16s16s", 0x42, user, serverpw, userpw)
        connection.send(packet)

    def sendMouse(self, position=(0.0, 0.0), velocity=(0.0, 0.0)):
        packet = struct.pack("=Bffff", 0x44, position[0], position[1],
                                            velocity[0], velocity[1])
        connection.send(packet)

    def sendKeyStatus(self, key, status):
        packet = struct.pack("=BBB", 0x43, key, status)
        connection.send(packet)

    def parse(self):
        list = connection.parse()
        for i in list:
            if i.name == "message":
                print i.message
            elif i.name == "status":
                for j in i.strings:
                    print j
            elif i.name.startswith("update"):
                #check wether the object exists
                if i.id in self.gamestatus["objects"]:
                    updated = self.gamestatus["objects"][i.id]
                elif i.name == "update":
                    #if object does not exist, create it, but only if the data
                    #is complete
                    updated = self.gamestatus["objects"][i.id] = {}
                else:
                    #Discard the packet and continue processing
                    print i.name, " packet with invalid ID recieved"
                    continue
                if i.name == "updatePos" or i.name == "update":
                    updated["pos"] = [i.posx, i.posy]
                    updated["vel"] = (i.velx, i.vely)
                if i.name == "updateGfx" or i.name == "update":
                    updated["gfx"] = i.gfx
                    updated["color"] = (i.colR, i.colG, i.colB)
            elif i.name == "delete":
                if i.id in self.gamestatus.objects:
                    del self.gamestatus["objects"][i]
                else:
                    #The server tries to delete an object that does not exist
                    print "The object with id %i does not exist" %(i.id)
            elif i.name == "loginAck":
                self.gamestatus.status = i.status
            elif i.name == "GTFO":
                raise GTFOException()

    def update(self, time):
        for obj in self.gamestatus["objects"].itervalues():
            obj["pos"][0] += obj["vel"][0]*time
            obj["pos"][1] += obj["vel"][1]*time

    def __del__(self):
        connection.close()

def status(stringbuffer):
    packet = connection.NetworPacket('status')
    packet.strings = []
    buffer = slength = stringbuffer.read(1)
    if not len(slength) == 1:
        raise connection.StreamIncompleteException(slength)
    length = struct.unpack('B', buffer)[0]
    while length > 0:
        slength = stringbuffer.read(2)
        buffer += slength
        if not slength == 2:
            raise connection.StreamIncompleteException(buffer)
        length = struct.unpack('H', slength)[0]
        string = stringbuffer.read(length)
        if len(string) < length:
            buffer += string
            raise connection.StreamIncompleteException(buffer)
        packet.strings.append(string)
    return packet

def message(stringbuffer):
    slength = stringbuffer.read(2)
    if not len(slength) == 2:
        raise connection.StreamIncompleteException(slength)
    length = struct.unpack('H', slength)[0]
    string = stringbuffer.read(length)
    if len(string) < length:
        raise connection.StreamIncompleteException(slength+string)
    packet = connection.NetworkPacket('message')
    packet.message = string
    return packet

class GTFOException(Exception):
    def __str__(self):
        return "GoD says: GTFO!!1!!"
