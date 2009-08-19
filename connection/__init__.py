import sys
import socket
import errno
import collections
import struct

import StringBuffer
from NIOBuffer import *

_connected = False
_conn = socket.socket()
_conn.setblocking(0)
#_buff = StringBuffer.StringBuffer()
_buff = NIOBuffer()

"""
This member conntains all rules for packet processing
The index is the package-header value and every entry must be of the form:
{
'name': <the name for the NetworkPacket
'processor': <either a sqequence of strings for use in the struct package or a
              function.
              The first parameter of the string-sequence is the value for the
              struct package every following value are the names of the values
              The function must raise a StreamIncomplete Exception if the
              Networkpacket is incomplete.
              Otherwise it should return the NetworkPacket.
}
"""
rules = dict()
magic_number = "\x00"
buffsize = 65536#8192#65536#32768#16384

def connected():
    return _connected

def connect(host, port):
    _conn.connect((host, port))
    _connected = True

def parse():
    try:
        _buff.append(_conn.recv(buffsize))
    except socket.error as e:
        if e.errno == 115:
            pass #This error means everything is going alright
        elif e.errno == 11:
            pass #This means that there is nothing to read
        else:
            raise e
    else:
        while True:
            position = _buff.getPosition()
            try:
                byte = _buff.read(1)
            except OutOfStreamException as e:
                _buff.seek(position)
            if byte == magic_number:
                try:
                    header = _buff.read(1)
                except OutOfStreamException as e:
                    _buff.seek(position)
                if header in rules:
                    rule = rules[header]
                    if isinstance(rule['processor'], collections.Callable):
                        try:
                            yield rule['processor'](_buff)
                        except StreamIncompleteException as e:
                            _buff.seek(position)
                            break
                    elif isinstance(rule['processor'], collections.Sequence):
                        size = struct.calcsize(rule['processor'][0])
                        try:
                            packet = _buff.read(size)
                        except OutOfStreamException as e:
                            #If this happens the packet is incomplete
                            _buff.seek(position)
                            break
                        tuple = struct.unpack(rule['processor'][0], packet)
                        packet = NetworkPacket(rule['name'])
                        for i in xrange(len(tuple)):
                            packet.__dict__[rule['processor'][i+1]] = tuple[i]
                        yield packet
                else:
                    _conn.close()
                    raise StreamError("Expected header, but got shit!")
            else:
                _conn.close()
                raise StreamError("Expected magic byte, but got shit!")
        _buff.reset()
        return

def send(stream):
    _conn.setblocking(1)
    _conn.send(magic_number + stream)
    _conn.setblocking(0)

def close():
    _conn.close()

class NetworkPacket(object):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        buff = 'NetworkPacket:['
        for i in self.__dict__:
            if not i.startswith('_'):
                buff += i + ': ' + repr(self.__dict__[i]) + ', '
        buff += ']'
        return buff

class StreamIncompleteException(Exception):
    pass

class MalformedPacketException(Exception):
    def __init__(self):
        pass
    def __str__(self):
        return "MalformedPacket"

class StreamError(Exception):
    def __init__(self, value):
        self.error = value
    def __str__(self):
        return repr(self.error)