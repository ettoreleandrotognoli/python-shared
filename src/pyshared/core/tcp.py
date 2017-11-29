import json
import socket

from pyshared.core.utils import mdebug
from rx import Observable
from rx import Observer
from rx.concurrency import ThreadPoolScheduler
from rx.subjects import Subject


class TCPServerConnection(Observer):
    def __init__(self, server: 'TCPServer', sock: socket.socket):
        self.running = False
        self.server = server
        self.socket = sock
        self._input_stream = Subject()
        self._output_stream = Subject()

    def get_input_stream(self) -> Observable:
        return self._input_stream

    input_stream = property(get_input_stream)

    def get_output_stream(self) -> Observer:
        return self._output_stream

    output_stream = property(get_output_stream)

    @mdebug
    def start(self, scheduler: ThreadPoolScheduler):
        Observable.create(self.run) \
            .subscribe_on(scheduler) \
            .subscribe(self.input_stream)
        self._output_stream.subscribe_on(scheduler) \
            .subscribe(self)

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
    def __init__(self,
                 serializer=json,
                 encoding='utf-8',
                 buffer_size: int = 2 ** 10):
        self.running = False
        self.thread = None
        self.buffer_size = buffer_size
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_stream = Subject()

    def connect(self, ip: str, port: int, backlog: int = 1):
        self.socket.bind((ip, port))
        self.socket.listen(backlog)

    @mdebug
    def start(self, scheduler: ThreadPoolScheduler):
        Observable.create(self.loop) \
            .map(lambda e: TCPServerConnection(self, e)) \
            .subscribe_on(scheduler) \
            .subscribe(self.client_stream)

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
    def __init__(self,
                 serializer=json,
                 encoding='utf-8',
                 buffer_size=2 ** 10):
        self.running = False
        self.buffer_size = buffer_size
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.thread = None
        self._input_stream = Subject()
        self._output_stream = Subject()

    def connect(self, ip: str, port: int):
        self.socket.connect((ip, port))

    def get_input_stream(self) -> Observable:
        return self._input_stream

    input_stream = property(get_input_stream)

    def get_output_stream(self) -> Observer:
        return self._output_stream

    output_stream = property(get_output_stream)

    @mdebug
    def start(self, scheduler: ThreadPoolScheduler):
        self._output_stream.subscribe_on(scheduler).subscribe(self)
        Observable.create(self.loop).subscribe_on(scheduler).subscribe(self._input_stream)

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
