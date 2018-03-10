import socket
from typing import Iterable

from pyshared.common.utils import mdebug
from rx import Observable
from rx import Observer


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
