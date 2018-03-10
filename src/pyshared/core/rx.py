import socket
from typing import Iterable

from pyshared.core.api import *
from pyshared.core.utils import mdebug
from rx import Observable
from rx import Observer
from rx.internal import extensionmethod


@extensionmethod(Observable)
def safe_map(self, map_function, handler=lambda x: None):
    def wrapper(*args, **kwargs):
        try:
            return Observable.just(map_function(*args, **kwargs))
        except Exception as ex:
            handler(ex)
            return Observable.empty()

    return self.flat_map(wrapper)


class ReactiveSharedResourcesServer(object):
    def __init__(self, shared_manager: SharedResourcesManager):
        self.shared_manager = shared_manager

    def __call__(self, command: Command, handler=lambda x: None) -> Observable:
        try:
            result = command.exec(self.shared_manager)
            if isinstance(result, Observable):
                return result
            return Observable.just(result)
        except Exception as ex:
            handler(ex)
            return Observable.empty()


class TCPServerConnection(Observer):
    def __init__(self, server: 'TCPServer', sock: socket.socket):
        self.running = False
        self.server = server
        self.socket = sock

    def as_observable(self, scheduler=None) -> Observable:
        return Observable.from_(self.as_iterable(), scheduler=scheduler)

    def as_iterable(self) -> Iterable:
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

    def connect(self, ip: str, port: int, backlog: int = 1) -> 'TCPServer':
        self.socket.bind((ip, port))
        self.port = self.socket.getsockname()[1]
        self.socket.listen(backlog)
        return self

    def as_observable(self, scheduler=None) -> Observable:
        return Observable.from_(self.as_iterable(), scheduler=scheduler)

    def connect_as_observable(self, ip: str, port: int, backlog: int = 1, scheduler=None) -> Observable:
        self.connect(ip, port, backlog)
        return self.as_observable(scheduler)

    def connect_as_iterable(self, ip: str, port: int, backlog: int = 1) -> Iterable:
        self.connect(ip, port, backlog)
        return self.as_iterable()

    def as_iterable(self) -> Iterable:
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

    def connect(self, ip: str, port: int) -> 'TCPClient':
        self.socket.connect((ip, port))
        return self

    def as_observable(self, scheduler=None) -> Observable:
        return Observable.from_(self.as_iterable(), scheduler=scheduler)

    def as_iterable(self) -> Iterable:
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
