import socket

from pyshared.core.utils import mdebug
from rx import Observer


class TCPServerConnection(Observer):
    def __init__(self, server: 'TCPServer', sock: socket.socket):
        self.running = False
        self.server = server
        self.socket = sock

    @mdebug
    def __call__(self, observer):
        self.loop(observer)

    def as_iterable(self):
        self.running = True
        while self.running:
            data = self.socket.recv(self.server.buffer_size)
            if not data:
                self.close()
                self.running = False
            yield data

    @mdebug
    def loop(self, observer: Observer):
        self.running = True
        while self.running:
            self.run(observer)
        observer.on_completed()

    @mdebug
    def run(self, observer: Observer):
        data = self.socket.recv(self.server.buffer_size)
        if not data:
            return self.close()
        observer.on_next(data)

    @mdebug
    def stop(self):
        self.running = False
        self.socket.close()

    @mdebug
    def on_next(self, value):
        self.socket.send(value)

    @mdebug
    def on_error(self, error):
        print(error)

    @mdebug
    def on_completed(self):
        self.stop()


class TCPServer(object):
    def __init__(self, buffer_size: int = 2 ** 10):
        self.running = False
        self.thread = None
        self.buffer_size = buffer_size
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, ip: str, port: int, backlog: int = 1):
        self.socket.bind((ip, port))
        self.socket.listen(backlog)
        return self.loop

    def connect_as_iterable(self, ip: str, port: int, backlog: int = 1):
        self.socket.bind((ip, port))
        self.socket.listen(backlog)
        return self.as_iterable()

    def as_iterable(self):
        self.running = True
        while self.running:
            try:
                conn, addr = self.socket.accept()
                yield TCPServerConnection(self, conn)
            except Exception as ex:
                raise ex

    @mdebug
    def loop(self, observer: Observer):
        self.running = True
        while self.running:
            self.run(observer)
        observer.on_completed()

    @mdebug
    def run(self, observer: Observer):
        try:
            conn, addr = self.socket.accept()
            observer.on_next(conn)
        except Exception as ex:
            observer.on_error(ex)

    @mdebug
    def stop(self):
        self.running = False
        self.socket.close()


class TCPClient(Observer):
    def __init__(self, buffer_size=2 ** 10):
        self.running = False
        self.buffer_size = buffer_size
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, ip: str, port: int):
        self.socket.connect((ip, port))
        return self.loop

    @mdebug
    def loop(self, observer: Observer):
        self.running = True
        while self.running:
            self.run(observer)
        observer.on_completed()

    @mdebug
    def run(self, observer: Observer):
        data = self.socket.recv(self.buffer_size)
        if not data:
            return self.close()
        observer.on_next(data)

    @mdebug
    def close(self):
        self.running = False
        self.socket.close()

    @mdebug
    def on_next(self, value):
        self.socket.send(value)

    @mdebug
    def on_completed(self):
        self.close()

    @mdebug
    def on_error(self, error):
        print(error)
