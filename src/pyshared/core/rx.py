import socket

from pyshared.core.api import *
from pyshared.core.utils import mdebug
from rx import Observable
from rx import Observer


class ReactiveSharedResourcesServer(object):
    def __init__(self, shared_manager: SharedResourcesManager):
        self.shared_manager = shared_manager

    def __call__(self, command: Command) -> Observable:
        result = command.exec(self.shared_manager)
        return Observable.just(result)


class TCPServerConnection(Observer):
    def __init__(self, server: 'TCPServer', sock: socket.socket):
        self.running = False
        self.server = server
        self.socket = sock

    def as_observable(self, scheduler=None):
        return Observable.from_(self.as_iterable(), scheduler=scheduler)

    def as_iterable(self):
        self.running = True
        while self.running:
            data = self.socket.recv(self.server.buffer_size)
            if not data:
                self.stop()
                return
            yield data

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
        self.port = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, ip: str, port: int, backlog: int = 1):
        self.socket.bind((ip, port))
        self.port = self.socket.getsockname()[1]
        self.socket.listen(backlog)
        return self

    def as_observable(self, scheduler=None) -> Observable:
        return Observable.from_(self.as_iterable(), scheduler=scheduler)

    def connect_as_observable(self, ip: str, port: int, backlog: int = 1, scheduler=None):
        self.connect(ip, port, backlog)
        return self.as_observable(scheduler)

    def connect_as_iterable(self, ip: str, port: int, backlog: int = 1):
        self.connect(ip, port, backlog)
        return self.as_iterable()

    def as_iterable(self):
        self.running = True
        while self.running:
            try:
                conn, addr = self.socket.accept()
                yield TCPServerConnection(self, conn)
            except Exception as ex:
                self.stop()
                raise ex

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
        return self

    def as_observable(self, scheduler=None):
        return Observable.from_(self.as_iterable(), scheduler=scheduler)

    def as_iterable(self):
        self.running = True
        while self.running:
            data = self.socket.recv(self.buffer_size)
            if not data:
                self.stop()
                return
            yield data

    def stop(self):
        self.running = False
        self.socket.close()

    @mdebug
    def on_next(self, value):
        self.socket.send(value)

    @mdebug
    def on_completed(self):
        self.stop()

    @mdebug
    def on_error(self, error):
        print(error)
