import multiprocessing
import time
import unittest

from pyshared.core.rx import TCPClient
from pyshared.core.rx import TCPServer
from pyshared.core.rx import TCPServerConnection
from pyshared.core.utils import fdebug
from pyshared.core.utils import map_debug
from rx import Observable
from rx.concurrency import ThreadPoolScheduler
from rx.testing import marbles

m = marbles
optimal_thread_count = multiprocessing.cpu_count() + 1
pool_scheduler = ThreadPoolScheduler(optimal_thread_count)


class TCPTest(unittest.TestCase):
    received_package = None

    def test_send_receive(self):
        total_clients = 1
        test_case = self
        test_package = dict(a=1, b=2)

        @fdebug
        def process(con: TCPServerConnection):
            print('new connection accepted')
            con.as_observable(pool_scheduler) \
                .map(lambda e: e.decode('utf-8')) \
                .map(map_debug) \
                .map(lambda e: e.encode('utf-8')) \
                .subscribe(con)

        server = TCPServer()
        server.connect('0.0.0.0', 0, backlog=10)
        port = server.port
        server.as_observable(pool_scheduler) \
            .subscribe(on_next=process, on_error=print)

        for i in range(total_clients):
            client = TCPClient()
            client_id = i
            client.connect('127.0.0.1', port) \
                .as_observable(pool_scheduler) \
                .map(lambda e: e.decode('utf-8')) \
                .subscribe(on_next=lambda e: print('client-%d receive -> ' % i, e), on_error=print)
            time.sleep(0.5)
            Observable.from_marbles('a-------------b--------------c-------------|') \
                .map(fdebug(lambda e: print('client-%d sending ->' % client_id, e) or e)) \
                .map(lambda e: e.encode('utf-8')) \
                .subscribe(client)
        time.sleep(10)
        server.stop()
        time.sleep(2)
        test_case.assertDictEqual(self.received_package, test_package)
