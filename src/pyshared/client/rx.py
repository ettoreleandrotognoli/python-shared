import socket
from typing import Iterable

from pyshared.common.encoding import parse_encoding
from pyshared.common.package import parse_parser
from pyshared.common.rx import BuffAndSplit
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


class ResourceAdapter(object):
    def __init__(self, manager, resource_name, method=None):
        self.manager = manager
        self.method = method
        self.resource_name = resource_name

    def __getattr__(self, item):
        if self.method is not None:
            raise Exception()
        return ResourceAdapter(
            manager=self.manager,
            method=item,
            resource_name=self.resource_name
        )

    def __call__(self, *args, **kwargs):
        if self.method is None:
            raise Exception()
        package = dict(
            cmd='call',
            method=self.method,
            resource_name=self.resource_name,
            args=args,
            kwargs=kwargs
        )
        return self.manager.send(package)


class RemoteResourceManager(object):
    def __init__(self, client_factory: TCPClient,
                 delimiter=b'\r\n',
                 encoding=parse_encoding('utf-8'),
                 parser=parse_parser('json')):
        self.encode_func, self.decode_func = encoding
        self.to_pack, self.from_pack = parser
        self.client_factory = client_factory
        self.delimiter = delimiter

    def send(self, pack, scheduler=None) -> Observable:
        connection = self.client_factory()
        return Observable.from_([pack]) \
            .map(self.to_pack) \
            .map(self.encode_func) \
            .map(lambda e: e + self.delimiter) \
            .map(connection.on_next) \
            .flat_map(connection.as_observable(scheduler=scheduler)) \
            .flat_map(BuffAndSplit(delimiter=self.delimiter)) \
            .map(self.decode_func) \
            .map(self.from_pack)

    def __getitem__(self, item):
        return ResourceAdapter(self, item)

    def __setitem__(self, key, value):
        package = dict(
            resource_name=key,
            value=value,
            cmd='set'
        )
        return self.send(package)

    def __delitem__(self, key):
        package = dict(
            resource_name=key,
            cmd='del'
        )
        return self.send(package)

    def __iter__(self):
        package = dict(
            cmd='list'
        )
        return self.send(package)
