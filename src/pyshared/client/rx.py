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


class ResourceAdapter():
    def __init__(self, manager, resource_name):
        self.manager = manager
        self.resource_name = resource_name

    def __call__(self, *args, **kwargs):
        package = dict(
            cmd='call',
            resource_name=self.resource_name,
            args=args,
            kwargs=kwargs
        )


class RemoteResourceManager():
    def __init__(self, client_factory: TCPClient):
        self.client_factory = client_factory

    def __getitem__(self, item):
        return ResourceAdapter(self, item)

    def __setitem__(self, key, value):
        package = dict(
            resource_name=key,
            value=value,
            cmd='set'
        )

    def __delitem__(self, key):
        package = dict(
            resource_name=key,
            cmd='del'
        )

    def __iter__(self):
        package = dict(
            cmd='list'
        )
