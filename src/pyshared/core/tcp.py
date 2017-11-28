import json
import socket
import threading

from rx import Observable
from rx import Observer
from rx.subjects import Subject


class TCPMixin(object):
    def __init__(self, serializer, encoding):
        self.serializer = serializer
        self.encoding = encoding

    def parse_data(self, data) -> dict:
        parsed_data = self.serializer.loads(data.decode(self.encoding))
        return parsed_data

    def prepare_data(self, data):
        prepared = self.serializer.dumps(data) + "\n"
        return prepared.encode(self.encoding)


class TCPServerConnAdapter(Observer):
    def __init__(self, server: 'TCPServer', sock: socket.socket):
        self.server = server
        self.socket = sock

    def on_next(self, value):
        parsed = self.server.parse_data(value)
        self.socket.send(parsed)

    def on_error(self, error):
        pass

    def on_completed(self):
        self.socket.close()


class TCPServer(Observable, TCPMixin):
    observer = None

    def __init__(self,
                 serializer=json,
                 encoding='utf-8',
                 buffer_size: int = 2 ** 10):
        super().__init__(serializer, encoding)
        self.running = False
        self.thread = None
        self.buffer_size = buffer_size
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.observer = Subject()

    def subscribe(self, *args, **kwargs):
        self.observer.subscribe(*args, **kwargs)

    def connect(self, ip: str, port: int, backlog: int = 1):
        self.socket.bind((ip, port))
        self.socket.listen(backlog)

    def start(self):
        self.thread = threading.Thread(target=self.loop)
        self.thread.start()

    def loop(self):
        self.running = True
        while self.running:
            self.run()

    def stop(self):
        self.running = False
        self.socket.close()
        self.thread.join()

    def run(self):
        try:
            conn, addr = self.socket.accept()
            observer = TCPServerConnAdapter(self, conn)
            self.observer.on_next((observer, None))
            while 1:
                data = conn.recv(self.buffer_size)
                if not data: break
                shared_package = self.parse_data(data)
                self.observer.on_next((observer, shared_package))
            self.observer.on_completed()
        except Exception as ex:
            self.observer.on_error(ex)
        finally:
            conn.close()


class TCPClient(Observer, Observable, TCPMixin):
    def __init__(self,
                 serializer=json,
                 encoding='utf-8',
                 buffer_size=2 ** 10):
        super().__init__(serializer, encoding)
        self.running = False
        self.buffer_size = buffer_size
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.thread = None
        self.observer = Subject()

    def connect(self, ip: str, port: int):
        self.socket.connect((ip, port))

    def subscribe(self, *args, **kwargs):
        self.observer.subscribe(*args, **kwargs)

    def start(self):
        self.thread = threading.Thread(target=self.loop())
        self.thread.start()

    def loop(self):
        self.running = True
        while self.running:
            self.run()

    def run(self):
        data = self.socket.recv(self.buffer_size)
        parsed = self.parse_data(data)
        self.observer.on_next((self, parsed))

    def close(self):
        self.socket.close()

    def on_next(self, value):
        self.send(value)

    def on_completed(self):
        self.close()

    def on_error(self, error):
        print(error)

    def send(self, data):
        self.socket.send(self.prepare_data(data))
