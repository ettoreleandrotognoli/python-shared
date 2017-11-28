import json
import socket
import threading

from rx import Observer


class TCPServer(object):
    encoding = 'utf-8'
    serializer = json

    def __init__(self, observer: Observer, buffer_size: int = 2 ** 10):
        self.running = False
        self.thread = None
        self.buffer_size = buffer_size
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.observer = observer

    def connect(self, ip: str, port: int, backlog: int = 1):
        self.socket.bind((ip, port))
        self.socket.listen(backlog)

    def parse_data(self, data) -> dict:
        parsed_data = self.serializer.loads(data.decode(self.encoding))
        return parsed_data

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

            def send_response(data):
                conn.send(data)

            while 1:
                data = conn.recv(self.buffer_size)
                if not data: break
                shared_package = self.parse_data(data)
                self.observer.on_next((*shared_package, send_response))
            self.observer.on_completed()
        except Exception as ex:
            self.observer.on_error(ex)
        finally:
            conn.close()


class TCPClient(object):
    encoding = 'utf-8'
    serializer = json

    def __init__(self, buffer_size=2 ** 10):
        self.buffer_size = buffer_size
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, ip: str, port: int):
        self.socket.connect((ip, port))

    def close(self):
        self.socket.close()

    def prepare_data(self, data):
        prepared = self.serializer.dumps(data) + "\n"
        return prepared.encode(self.encoding)

    def send(self, data):
        self.socket.send(self.prepare_data(data))

    def list_resources(self):
        data = self.socket.recv(self.buffer_size)
        return self.serializer.loads(data)

    def call_resource(self, resource_id, *args, **kwargs):
        if isinstance(resource_id, str):
            resource_id = [resource_id]
        package = self.call_template.format(
            '.'.join(resource_id),
            self.serializer.dumps(args),
            self.serializer.dumps(kwargs),
        )
        self.socket.send(package)
        data = self.socket.recv(self.buffer_size)
        return self.serializer.loads(data)
