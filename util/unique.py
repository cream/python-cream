"""
    Unique protocol
    ---------------

    When a client connects:

        Server accepts request.
        Client sends `ping` message.
        Server responds with `pong` message.
"""

import sys
import os
import socket

from lxml import etree

import gobject
import glib

import gpyconf.backends._xml.xmlserialize as xmlserialize

SOCKET_TEMPLATE = 'var/run/cream/%s.sock'
PONG_TIMEOUT = 1000 # TODO

class UniqueApplication(gobject.GObject):
    @classmethod
    def get(cls, ident):
        """
            :param ident: A string to identify an application. Should be unique system-wide.
        """
        socket_path = SOCKET_TEMPLATE % ident
        if os.path.exists(socket_path):
            # This application is already running. I'm a client.
            print '--- client'
            return UniqueApplicationClient(ident)
        else:
            # I'm the server.
            print '--- server'
            return UniqueApplicationServer(ident)

    def __init__(self, ident):
        gobject.GObject.__init__(self)
        self.ident = ident
        self.socket = None
        self.socket_path = SOCKET_TEMPLATE % ident

    def run(self):
        raise NotImplementedError()

    def quit(self):
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)

gobject.type_register(UniqueApplication)
gobject.signal_new('already-running', UniqueApplication, gobject.SIGNAL_RUN_LAST, \
                   gobject.TYPE_PYOBJECT, ())

def build_message(type, node=None):
    """
        Return a XML-serialized message as a string. Its type is *type*,
        its content node is *node*.
    """
    msg = etree.Element('message', type=type)
    if node is not None:
        msg.append(node)
    return etree.tostring(msg)

def serialize_message(type, obj):
    return build_message(type, xmlserialize.serialize(obj, return_string=False))

class States(object):
    NONE = 'none'
    HANDSHAKE_DONE = 'handshake done'

class UniqueError(Exception):
    pass

class Handler(object):
    def __init__(self):
        self.buffer = ''

    def handle(self, node):
        raise NotImplementedError()

    def handle_message(self, message):
        # It's XML, parse it.
        node = etree.fromstring(message)
        self.handle(node)

    def handle_data(self):
        """
            I have new data. Read it.
        """
        # Read all available data.
        while True:
            try:
                self.buffer += self.conn.recv(1024)
            except socket.error:
                # TODO: ouch?
                break
        # Split at nullbyte
        messages = self.buffer.split('\0')
        # Last element isn't empty? So we received an incomplete message,
        # leave the last element in the buffer. Otherwise, clear it.
        self.buffer = messages.pop()
        # Handle all messages.
        for message in messages:
            self.handle_message(message)

class Client(Handler):
    def __init__(self, conn):
        Handler.__init__(self)
        self.conn = conn
        self.state = States.NONE
        self.buffer = ''

    def handle_ping(self, node):
        self.expect_type(node, 'ping')
        # send a `pong` message.
        self.send_message('pong')

    def expect_type(self, node, type):
        if node.attrib.get('type') != type:
            raise UniqueError('%r = stupid client. Expected %s, got %s' % (self, type, node.attrib.get('type')))

    def handle(self, node):
        {
            States.NONE: self.handle_ping,
        }[self.state](node)

    def send(self, text):
        """
            Send *text* and end with a null byte.
        """
        self.conn.sendall('%s\0' % text)

    def send_message(self, type, node=None):
        self.send(build_message(type, node))

class UniqueApplicationServer(UniqueApplication):
    def __init__(self, ident):
        UniqueApplication.__init__(self, ident)
        self.clients = {} # { conn: client }

    def run(self):
        # Create a UNIX socket
        self.socket = socket.socket(socket.AF_UNIX)
        self.socket.setblocking(False)
        self.socket.bind(self.socket_path)
        # Doit!
        self.socket.listen(1)
        # Connect IO callbacks
        glib.io_add_watch(self.socket,
                             glib.IO_IN,
                             self._listen_callback)

    def _listen_callback(self, source, condition):
        print 'Yay listening.'
        conn, addr = self.socket.accept()
        conn.setblocking(False)
        print 'Gotcha:', conn, addr
        # add the client
        client = Client(conn)
        self.add_client(client)
        # I want to get the data.
        glib.io_add_watch(conn,
                        glib.IO_IN | glib.IO_HUP,
                        self._data_callback)
        return True

    def add_client(self, client):
        self.clients[client.conn] = client
        print 'Added client %r ...' % client

    def remove_client(self, client):
        del self.clients[client.conn]
        print 'Removed client %r ...' % client

    def get_client_by_conn(self, conn):
        return self.clients[conn]

    def _data_callback(self, source, condition):
        # HUP? So our client disappeared. Sad thing.
        client = self.get_client_by_conn(source)
        if condition & glib.IO_HUP:
            source.close()
            self.remove_client(client)
            return False
        else:
            client.handle_data()
            return True

class UniqueApplicationClient(UniqueApplication, Handler):
    def __init__(self, ident):
        UniqueApplication.__init__(self, ident)
        Handler.__init__(self)
        self.handshake_done = False

    def send(self, text):
        """
            Send *text* and end with a null byte.
        """
        self.socket.sendall('%s\0' % text)

    def send_message(self, type, node=None):
        self.send(build_message(type, node))

    def send_ping(self):
        self.send_message('ping')
        # if we haven't received a pong in $PONG_TIMEOUT ms,
        # consider the server down.
        gobject.timeout_add(PONG_TIMEOUT, self.check_handshake)

    def check_handshake(self):
        """
            Do we have a valid handshake yet?
            If not, the server is down. Please replace.
            Otherwise, raise the `already-running` signal.
        """
        if not self.handshake_done:
            self.replace_server()
        else:
            self.already_running()
        return False

    def replace_server(self):
        """
            For some reason, the server is offline. Replace it.
        """
        print 'OMG REPLACE'
        # TODO

    def already_running(self):
        result = self.emit('already-running')
        print 'RESULT IS %r' % result

    def run(self):
        # Create a UNIX socket
        self.socket = self.conn = socket.socket(socket.AF_UNIX) # Set `self.conn` to make `Handler` happy
        self.socket.setblocking(False)
        self.socket.connect(self.socket_path)
        # Connect IO callbacks
        glib.io_add_watch(self.socket,
                             glib.IO_IN,
                             self._data_callback)
        # Send ping message.
        self.send_ping()

    def _data_callback(self, source, condition):
        self.handle_data()
        return True

    def handle(self, node):
        {
            'pong': self.handle_pong,
        }[node.attrib['type']](node)

    def handle_pong(self, node):
        # handshake done!
        self.handshake_done = True
