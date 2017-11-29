import json
import multiprocessing
import time
import unittest

from pyshared.core.tcp import TCPClient
from pyshared.core.tcp import TCPServer
from pyshared.core.tcp import TCPServerConnection
from pyshared.core.utils import fdebug
from rx import Observable
from rx.concurrency import ThreadPoolScheduler

port = 8000
optimal_thread_count = multiprocessing.cpu_count() + 1
pool_scheduler = ThreadPoolScheduler(optimal_thread_count)


class TCPTest(unittest.TestCase):
    received_package = None

    def test_send_receive(self):
        test_case = self
        test_package = dict(a=1, b=2)
        client = TCPClient()

        @fdebug
        def process(con: TCPServerConnection):
            con.start(pool_scheduler)
            con.get_input_stream() \
                .observe_on(pool_scheduler) \
                .subscribe_on(pool_scheduler) \
                .subscribe(lambda e: print('server receive ->', e))
            Observable.from_([{'c': 3}, {'d': 4}]) \
                .observe_on(pool_scheduler) \
                .map(json.dumps) \
                .map(lambda e: e.encode('utf-8')) \
                .subscribe_on(pool_scheduler) \
                .subscribe(con.get_output_stream())

        server = TCPServer()
        server.connect('0.0.0.0', port)
        server.start(pool_scheduler)
        server.client_stream.subscribe(on_next=process)

        client.connect('127.0.0.1', port)
        client.start(pool_scheduler)
        client.get_input_stream() \
            .observe_on(pool_scheduler) \
            .map(lambda e: e.deocde('utf-8')) \
            .map(json.loads) \
            .subscribe_on(pool_scheduler) \
            .subscribe(on_next=lambda e: print('client receive -> ', e))
        Observable.from_([{'a': 1}, {'b': 2}]) \
            .observe_on(pool_scheduler) \
            .map(json.dumps) \
            .map(lambda e: e.encode('utf-8')) \
            .subscribe_on(pool_scheduler) \
            .subscribe(client.get_output_stream())
        time.sleep(2)
        server.stop()
        test_case.assertDictEqual(self.received_package, test_package)
