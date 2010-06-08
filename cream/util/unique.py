"""
    Unique protocol
    ---------------

    When a client connects:

        Server accepts request.
        Client sends `ping` message.
        Server responds with `pong` message.
        Client sends `notify` message.
        Server responds with `kthxbai` message.
        Client responds with `cu` message and dies.
"""

import sys
import os
import socket

from lxml import etree

import gobject
import glib

from xmlserialize import serialize, unserialize

SOCKET_TEMPLATE = os.path.expanduser('~/.local/var/run/cream/%s.sock')
PONG_TIMEOUT = 100 # = 100 ms.

class UniqueApplication(gobject.GObject):
    def __init__(self, ident):
        gobject.GObject.__init__(self)
        self._ident = ident
        self._setup_unique()

    def _setup_unique(self):
        self._unique_manager = UniqueManager.get(self, self._ident)
        self._unique_manager.run() # TODO

    def _replace_server(self):
        """
            I was a client before, but now I am a server. YAY!
        """
        self._unique_manager.quit()
        self._setup_unique()

    def quit(self):
        self._unique_manager.quit()

gobject.type_register(UniqueApplication)
gobject.signal_new('already-running', UniqueApplication, gobject.SIGNAL_RUN_LAST, \
                   gobject.TYPE_PYOBJECT, ())
gobject.signal_new('start-attempt', UniqueApplication, gobject.SIGNAL_RUN_LAST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))

class UniqueManager(object):
    @classmethod
    def get(cls, app, ident):
        """
            :param ident: A string to identify an application. Should be unique system-wide.
        """
        socket_path = SOCKET_TEMPLATE % ident
        if os.path.exists(socket_path):
            # This application is already running. I'm a client.
            return UniqueManagerClient(app, ident)
        else:
            # I'm the server.
            return UniqueManagerServer(app, ident)

    def __init__(self, app, ident):
        self.sources = set()
        self.app = app
        self.ident = ident
        self.socket = None
        self.socket_path = SOCKET_TEMPLATE % ident

    def run(self):
        raise NotImplementedError()

    def quit(self):
        try:
            self.socket.close()
        except socket.error:
            pass
        # remove all glib sources
        for source in self.sources:
            glib.source_remove(source)

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
    return build_message(type, serialize(obj, return_string=False))

class States(object):
    NONE = 'none'
    HANDSHAKE_DONE = 'handshake done'
    DONE = 'done'

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
                new = self.conn.recv(1024)
                if not new:
                    break
                self.buffer += new
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
    def __init__(self, manager, conn):
        Handler.__init__(self)
        self.manager = manager
        self.conn = conn
        self.state = States.NONE
        self.buffer = ''
        self.sources = set()

    def handle_ping(self, node):
        self.expect_type(node, 'ping')
        # send a `pong` message.
        self.send_message('pong')
        # and set the new state.
        self.state = States.HANDSHAKE_DONE

    def remove(self):
        for source in self.sources:
            glib.source_remove(source)

    def handle_notify(self, node):
        self.expect_type(node, 'notify')
        # get the data.
        data = unserialize(node[0])
        # emit the signal.
        self.manager.app.emit('start-attempt', data)
        # send the message.
        self.send_message('kthxbai')
        self.state = States.DONE

    def handle_argh(self, node):
        self.expect_type(node, 'cu')
        # self-destruct.
        self.conn.close()
        self.manager.remove_client(self)

    def expect_type(self, node, type):
        if node.attrib.get('type') != type:
            raise UniqueError('%r = stupid client. Expected %s, got %s' % (self, type, node.attrib.get('type')))

    def handle(self, node):
        {
            States.NONE: self.handle_ping,
            States.HANDSHAKE_DONE: self.handle_notify,
            States.DONE: self.handle_argh,
        }[self.state](node)

    def send(self, text):
        """
            Send *text* and end with a null byte.
        """
        self.conn.sendall('%s\0' % text)

    def send_message(self, type, node=None):
        self.send(build_message(type, node))

class UniqueManagerServer(UniqueManager):
    def __init__(self, app, ident):
        UniqueManager.__init__(self, app, ident)
        self.clients = {} # { conn: client }

    def quit(self):
        UniqueManager.quit(self)
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)

    def run(self):
        # Create a UNIX socket
        if not os.path.exists(os.path.dirname(self.socket_path)):
            os.makedirs(os.path.dirname(self.socket_path))
        self.socket = socket.socket(socket.AF_UNIX)
        self.socket.setblocking(False)
        self.socket.bind(self.socket_path)
        # Doit!
        self.socket.listen(1)
        # Connect IO callbacks
        self.sources.add(glib.io_add_watch(self.socket,
                             glib.IO_IN,
                             self._listen_callback))

    def _listen_callback(self, source, condition):
        conn, addr = self.socket.accept()
        conn.setblocking(False)
        # add the client
        client = Client(self, conn)
        self.add_client(client)
        # I want to get the data.
        client.sources.add(glib.io_add_watch(conn,
                        glib.IO_IN | glib.IO_HUP,
                        self._data_callback))
        return True

    def add_client(self, client):
        self.clients[client.conn] = client

    def remove_client(self, client):
        client.remove()
        del self.clients[client.conn]

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

class UniqueManagerClient(UniqueManager, Handler):
    def __init__(self, app, ident):
        UniqueManager.__init__(self, app, ident)
        Handler.__init__(self)
        self.handshake_done = False

    def send(self, text):
        """
            Send *text* and end with a null byte.
        """
        self.socket.sendall('%s\0' % text)

    def send_message(self, type, node=None):
        self.send(build_message(type, node))

    def send_serialized_message(self, type, obj):
        self.send(serialize_message(type, obj))

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
        # Kill the socket. :S
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)
        # Make my master replace me. :(
        self.app._replace_server()

    def already_running(self):
        result = self.app.emit('already-running')
        # serialize result, send notify message
        self.send_serialized_message('notify', result)

    def run(self):
        # Create a UNIX socket
        if not os.path.exists(os.path.dirname(self.socket_path)):
            os.makedirs(os.path.dirname(self.socket_path))
        self.socket = self.conn = socket.socket(socket.AF_UNIX) # Set `self.conn` to make `Handler` happy
        self.socket.setblocking(False)
        try:
            self.socket.connect(self.socket_path)
        except socket.error:
            # Socket error ... uhm, replace it!
            self.replace_server()
            return
        # Connect IO callbacks
        self.sources.add(glib.io_add_watch(self.socket,
                             glib.IO_IN,
                             self._data_callback))
        # Send ping message.
        self.send_ping()

    def _data_callback(self, source, condition):
        self.handle_data()
        return True

    def handle(self, node):
        {
            'pong': self.handle_pong,
            'kthxbai': self.handle_kthxbai,
        }[node.attrib['type']](node)

    def handle_pong(self, node):
        # handshake done!
        self.handshake_done = True

    def handle_kthxbai(self, node):
        # Server got our information, we can die now.
        self.send_message('cu')
        self.app.quit()

