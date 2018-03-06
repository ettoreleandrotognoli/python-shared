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

port = 8001
optimal_thread_count = multiprocessing.cpu_count() + 1
pool_scheduler = ThreadPoolScheduler(optimal_thread_count)


@fdebug
def print_and_return(v):
    print('server receive', v)
    return eval(v)


class TCPTest(unittest.TestCase):
    received_package = None

    def test_send_receive(self):
        test_case = self
        test_package = dict(a=1, b=2)

        @fdebug
        def process(con: TCPServerConnection):
            print('new connection accepted')
            Observable.create(con) \
                .observe_on(pool_scheduler) \
                .map(lambda e: e.decode('utf-8')) \
                .map(json.loads) \
                .map(print_and_return) \
                .map(json.dumps) \
                .map(lambda e: e.encode('utf-8')) \
                .subscribe_on(pool_scheduler) \
                .subscribe(con)

        server = TCPServer()
        Observable.create(server.connect('0.0.0.0', port, backlog=10)) \
            .observe_on(pool_scheduler) \
            .subscribe_on(pool_scheduler) \
            .subscribe(process)

        for i in range(2):
            client = TCPClient()
            Observable.create(client.connect('127.0.0.1', port)) \
                .observe_on(pool_scheduler) \
                .map(lambda e: e.decode('utf-8')) \
                .map(json.loads) \
                .subscribe_on(pool_scheduler) \
                .subscribe(on_next=lambda e: print('client-%d receive -> ' % i, e))
            time.sleep(0.5)
            Observable.from_(['time.sleep(0.2) or True', 'time.sleep(0.2) or \'fuu\''] * 3) \
                .zip(Observable.interval(1000), lambda a, b: a) \
                .map(fdebug(lambda e: print('client-%d sending ->' % i, e) or e)) \
                .map(json.dumps) \
                .map(lambda e: e.encode('utf-8')) \
                .subscribe(client)
        time.sleep(10)
        server.stop()
        time.sleep(2)
        test_case.assertDictEqual(self.received_package, test_package)
