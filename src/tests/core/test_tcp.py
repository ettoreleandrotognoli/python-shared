import multiprocessing
import time
import unittest

from pyshared.client.rx import TCPClient
from pyshared.common.utils import fdebug
from pyshared.common.utils import map_debug
from pyshared.server.rx import TCPServer
from pyshared.server.rx import TCPServerConnection
from rx import Observable
from rx.concurrency import ThreadPoolScheduler
from rx.testing import marbles

address = "0.0.0.0"
m = marbles
optimal_thread_count = multiprocessing.cpu_count() * 2


class Schedulers:
    computation = ThreadPoolScheduler(optimal_thread_count)


class TCPTest(unittest.TestCase):
    received_package = None

    def test_send_receive(self):
        total_clients = 2
        result = []

        @fdebug
        def process(con: TCPServerConnection):
            con.as_observable(Schedulers.computation) \
                .map(lambda e: e.decode('utf-8')) \
                .map(map_debug) \
                .map(lambda e: e.encode('utf-8')) \
                .subscribe(con)

        server = TCPServer()
        server.connect(address, 0)
        port = server.port
        print('listening at %s:%d' % (address, port))
        server.as_observable(Schedulers.computation) \
            .subscribe(on_next=process, on_error=lambda e: print('error on server', e))

        clients = []
        Observable.from_(range(total_clients)) \
            .map(lambda e: TCPClient()) \
            .map(lambda e: e.connect('127.0.0.1', port)) \
            .subscribe(clients.append)

        print(clients)

        Observable.from_(clients) \
            .flat_map(lambda c: c.as_observable(Schedulers.computation)) \
            .map(lambda e: e.decode('utf-8')) \
            .subscribe(result.append)

        send_data = Observable.from_marbles('-a-b-c-|') \
            .map(lambda e: e.encode('utf-8')) \
            .subscribe
        Observable.from_(clients).subscribe(send_data)

        time.sleep(1)
        server.stop()
        self.assertEqual(['a', 'a', 'b', 'b', 'c', 'c'], result)
        del Schedulers.computation
